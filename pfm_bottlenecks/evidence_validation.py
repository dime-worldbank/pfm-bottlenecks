"""
Bottleneck Processor - Main processing engine for bottleneck evidence extraction and validation.
"""

import pandas as pd
from tqdm import tqdm
from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from pyspark.sql import SparkSession
from pfm_bottlenecks.service import Service
from pfm_bottlenecks.bottleneck_definitions import load_bottleneck_definition, get_schema
from pfm_bottlenecks.consts import LLM_MODEL, VALIDATION_SYSTEM_PROMPT

def build_validation_model(bottleneck_id: str, subschema: dict, subschema_index: int = 0):

    safe_name = f"{bottleneck_id}_{subschema_index}".replace('.', '_')

    # Dynamic enums from schema lists
    StrongCueEnum = Enum(
        f"StrongCue_{safe_name}",
        {name: name for name in subschema["strong_cues"]}
    )

    ModerateCueEnum = Enum(
        f"ModerateCue_{safe_name}",
        {name: name for name in subschema["moderate_cues"]}
    )

    FailureTypeEnum = Enum(
        f"FailureType_{safe_name}",
        {name: name for name in subschema.get("failure_types", [])} or {"none": "none"}
    )

    DecisionEnum = Enum(
        f"Decision_{safe_name}",
        {
            "relevant_feature": "relevant_feature",
            "relevant_feature_and_failure": "relevant_feature_and_failure",
            "irrelevant": "irrelevant",
            "abstain": "abstain",
        },
    )

    SubtypeEnum = Enum(
        f"Subtype_{safe_name}",
        {"other": "other", **{s: s for s in subschema.get("subtypes", [])}},
    )

    class BottleneckValidation(BaseModel):
        """
        Validation output for bottleneck {bottleneck_id}.
        Cues / failure types are constrained by the bottleneck's schema.
        """

        # Primary decisions
        is_bottleneck_evidence: bool = Field(
            ...,
            description=(
                f"Feature-based verdict for bottleneck {bottleneck_id}. "
                f"Should usually follow acceptance_rule: {subschema.get('acceptance_rule', '')}"
            ),
        )
        is_bottleneck_plus_failure: bool = Field(
            ...,
            description=(
                "Consequence-based verdict. True iff is_bottleneck_evidence and failure_present."
            ),
        )
        decision: DecisionEnum = Field(
            ...,
            description=(
                'Overall decision among {"relevant_feature",'
                ' "relevant_feature_and_failure", "irrelevant", "abstain"}.'
            ),
        )

        # Evidence for bottleneck features
        strong_cues: List[StrongCueEnum] = Field(
            default_factory=list,
            description="Which strong cues were found.",
        )
        moderate_cues: List[ModerateCueEnum] = Field(
            default_factory=list,
            description="Which moderate cues were found.",
        )
        hard_negative: bool = Field(
            False,
            description="True if any hard negative applies for this bottleneck.",
        )
        trigger_spans: List[str] = Field(
            default_factory=list,
            description=(
                "Verbatim phrases from the text that support bottleneck cues "
                "(must be substrings of the extracted evidence)."
            ),
        )
        subtype: SubtypeEnum = Field(
            SubtypeEnum.other,
            description="Subtype of the bottleneck, if applicable.",
        )

        # Evidence for failure/inefficiency
        failure_present: bool = Field(
            False,
            description="True if an explicit or clearly implied failure/inefficiency is present.",
        )
        failure_types: List[FailureTypeEnum] = Field(
            default_factory=list,
            description="Categorization of the failure/inefficiency mentioned.",
        )
        failure_spans: List[str] = Field(
            default_factory=list,
            description=(
                "Verbatim phrases supporting failure/inefficiency "
                "(must be substrings of the extracted evidence)."
            ),
        )

        rationale: str = Field(
            ...,
            description=(
                "2–3 sentence justification referencing trigger_spans/failure_spans; "
                "avoid speculation; no new facts."
            ),
        )

    return BottleneckValidation


class BottleneckProcessor:
    """
    Handles validation in a single pass.
    """

    def __init__(self, bottleneck_id: str, service: Service, model: str = LLM_MODEL):
        self.bottleneck_id = bottleneck_id
        self.service = service
        self.model = model
        self.schema = get_schema(bottleneck_id)
        self.definition = load_bottleneck_definition(bottleneck_id)
        self.validation_models = [
            build_validation_model(bottleneck_id, subschema, i)
            for i, subschema in enumerate(self.schema)
        ]

    def validate_extraction(
        self, extracted_text: str, node_id: int, chunk_id: int
    ) -> dict:
        if len(self.schema) == 1:
            return self._validate_single(extracted_text, node_id, chunk_id)
        else:
            return self._validate_multi(extracted_text, node_id, chunk_id)

    def _validate_single(
        self, extracted_text: str, node_id: int, chunk_id: int
    ) -> dict:
        prompt = self._build_validation_prompt(extracted_text, self.schema[0])

        validation = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=self.validation_models[0],
            system_message=VALIDATION_SYSTEM_PROMPT,
        )

        data = validation.model_dump(mode="json")
        data["node_id"] = node_id
        data["chunk_id"] = chunk_id
        data["bottleneck_id"] = self.bottleneck_id

        return data

    def _validate_multi(
        self, extracted_text: str, node_id: int, chunk_id: int
    ) -> dict:
        matched_subschemas = []
        subschema_results = []
        # TODO: Avoid using the loop here (high token usage). Find a better way for finding the appropriate subschema (could use semantic similarity with threshold)
        for i, subschema in enumerate(self.schema):
            prompt = self._build_validation_prompt(extracted_text, subschema)

            validation = self.service.execute(
                prompt=prompt,
                model=self.model,
                response_model=self.validation_models[i],
                system_message=VALIDATION_SYSTEM_PROMPT,
            )

            data = validation.model_dump(mode="json")
            subschema_name = subschema.get("subschema", f"subschema_{i}")
            data["subschema"] = subschema_name

            if data["is_bottleneck_evidence"]:
                matched_subschemas.append(subschema_name)

            subschema_results.append(data)

        return {
            "node_id": node_id,
            "chunk_id": chunk_id,
            "bottleneck_id": self.bottleneck_id,
            "matched_subschemas": matched_subschemas,
            "decision": len(matched_subschemas) > 0,
            "subschema_results": subschema_results,
        }

    def _build_validation_prompt(self, extracted_text: str, subschema: dict) -> str:
        """Build prompt for validating extracted evidence."""
        definition = self.definition

        custom_sections = ""
        if subschema.get("prompt_sections"):
            for section_name, section_text in subschema["prompt_sections"].items():
                custom_sections += (
                    f"\n{section_name.upper().replace('_', ' ')}:\n{section_text}\n"
                )

        return f"""You are validating extracted evidence for a Public Finance Management bottleneck.

            BOTTLENECK:
            {definition["name"]}

            DESCRIPTION:
            {definition["description"]}

            EXTENDED DEFINITION:
            {definition.get("extended_definition") or definition["description"]}

            VALIDATION CRITERIA:

            Strong Cues (any ONE is sufficient):
            {self._format_list(subschema["strong_cues"])}

            Moderate Cues (need TWO or more):
            {self._format_list(subschema["moderate_cues"])}

            Hard Negatives (REJECT if these apply):
            {self._format_list(subschema["hard_negatives"])}

            SCOPE LOCK:
            {subschema.get("scope_lock", "")}

            ACCEPTANCE RULE: {subschema["acceptance_rule"]}
            {custom_sections}
            EXTRACTED EVIDENCE TO VALIDATE:
            {extracted_text}

            TASK:
            1. Identify which cues are detected (strong, moderate, hard negatives)
            2. Extract trigger spans (diagnostic phrases) and failure spans (consequences)
            3. Apply the acceptance rule to make a decision
            4. Provide a detailed rationale

            Decision Types:
            - "relevant_feature": Cues met, no hard negatives
            - "relevant_feature_and_failure": Cues met + consequence/failure mentioned
            - "irrelevant": Hard negative detected or no qualifying cues
            - "abstain": Uncertain

            Be conservative. Quote verbatim from the extracted text.
            Return ONLY JSON that matches the schema you have been given.
            """

    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt."""
        return "\n".join(f"  - {item}" for item in items)

def run_validation(spark: SparkSession, service: Service, schema: str, bottleneck_id: str, overwrite: bool = False):
    """Validate extracted evidence against schema. Overwrites results each run."""

    extractions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_extractions"
    validated_results_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_validated_results"
    validated_results_table_exist = spark.catalog.tableExists(f"{schema}.{validated_results_table}")

    if validated_results_table_exist and not overwrite:
        print(f"Skipping evidence validation for {bottleneck_id} as table {schema}.{validated_results_table} already exists")
        return

    extractions_df = spark.table(f"{schema}.{extractions_table}").toPandas()
    has_evidence = extractions_df[extractions_df["extracted_evidence"].notna()]

    print(f"Loaded {len(has_evidence)} extractions with evidence for validation")

    if len(has_evidence) == 0:
        print("No extractions to validate")
        return

    processor = BottleneckProcessor(bottleneck_id, service)
    is_multi_subschema = len(processor.schema) > 1

    results = []
    total = len(has_evidence)

    print(f"Validating {total} extractions for bottleneck {bottleneck_id}...")

    for idx, row in tqdm(has_evidence.iterrows(), total=has_evidence.shape[0]):
        chunk_id = row["chunk_id"]
        node_id = row["node_id"]
        extracted_text = row["extracted_evidence"]

        try:
            row_dict = processor.validate_extraction(extracted_text, node_id, chunk_id)
            if is_multi_subschema:
                row_dict["is_bottleneck_evidence"] = row_dict["decision"]
            results.append(row_dict)
        except Exception as e:
            print(f"  Error validating chunk {chunk_id}: {str(e)}")
            error_result = {
                "node_id": node_id,
                "chunk_id": chunk_id,
                "bottleneck_id": bottleneck_id,
                "is_bottleneck_evidence": False,
                "rationale": f"Validation error: {str(e)}",
            }
            if is_multi_subschema:
                error_result.update({
                    "matched_subschemas": [],
                    "decision": False,
                    "subschema_results": [],
                })
            else:
                error_result.update({
                    "is_bottleneck_plus_failure": False,
                    "decision": "irrelevant",
                    "strong_cues": [],
                    "moderate_cues": [],
                    "hard_negative": False,
                    "trigger_spans": [],
                    "subtype": "other",
                    "failure_present": False,
                    "failure_types": [],
                    "failure_spans": [],
                })
            results.append(error_result)

    print(f"Completed validation: {total} extractions")

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{validated_results_table}")

    evidence_count = results_df["is_bottleneck_evidence"].sum()
    print(f"Results: {evidence_count}/{len(results_df)} validated as evidence")
