# Databricks notebook source
# MAGIC %pip install -U "pydantic>=2.4,<3" instructor openai azure-identity sentence-transformers

# COMMAND ----------

# MAGIC %run ./service

# COMMAND ----------

# MAGIC %run ./consts

# COMMAND ----------

# MAGIC %run ./bottleneck_schemas

# COMMAND ----------

# MAGIC %run ./bottleneck_definitions

# COMMAND ----------

"""
Bottleneck Processor - Main processing engine for bottleneck evidence extraction and validation.
"""

from typing import List
import pandas as pd
from tqdm import tqdm
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

def build_validation_model(bottleneck_id: str, schema: dict):

    # Dynamic enums from schema lists
    StrongCueEnum = Enum(
        f"StrongCue_{bottleneck_id.replace('.', '_')}",
        {name: name for name in schema["strong_cues"]}
    )

    ModerateCueEnum = Enum(
        f"ModerateCue_{bottleneck_id.replace('.', '_')}",
        {name: name for name in schema["moderate_cues"]}
    )

    FailureTypeEnum = Enum(
        f"FailureType_{bottleneck_id.replace('.', '_')}",
        {name: name for name in schema.get("failure_types", [])} or {"none": "none"}
    )

    DecisionEnum = Enum(
        f"Decision_{bottleneck_id.replace('.', '_')}",
        {
            "relevant_feature": "relevant_feature",
            "relevant_feature_and_failure": "relevant_feature_and_failure",
            "irrelevant": "irrelevant",
            "abstain": "abstain",
        },
    )

    SubtypeEnum = Enum(
        f"Subtype_{bottleneck_id.replace('.', '_')}",
        {"other": "other", **{s: s for s in schema.get("subtypes", [])}},
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
                f"Should usually follow acceptance_rule: {schema.get('acceptance_rule', '')}"
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
        """
        Initialize processor for a specific bottleneck.

        Args:
            bottleneck_id: Bottleneck ID (e.g., "2.1", "6.1")
            service: Service instance for LLM calls
            model: Model name for OpenAI (default: LLM_MODEL)
        """
        self.bottleneck_id = bottleneck_id
        self.service = service
        self.model = model
        self.schema = get_schema(bottleneck_id)
        self.definition = self._load_definition()
        self.validation_model = build_validation_model(bottleneck_id, self.schema)

    def _load_definition(self) -> dict:
        """Load bottleneck definition from centralized source."""
        data = load_bottlenecks()
        challenge_id = int(self.bottleneck_id.split(".")[0])
        challenge = data["challenges"][challenge_id]

        for bn in challenge["bottlenecks"]:
            if bn["id"] == self.bottleneck_id:
                return {
                    "id": bn["id"],
                    "name": bn["name"],
                    "description": bn["description"],
                    "extended_definition": bn.get("extended_definition", ""),
                    "challenge_name": challenge["name"],
                    "challenge_description": challenge["description"],
                }
        raise ValueError(f"Bottleneck {self.bottleneck_id} not found in definitions")


    def validate_extraction(
        self, extracted_text: str, node_id: int, chunk_id: int
    ) -> dict:
        """
        Validate extracted evidence against schema cues and hard negatives.

        Returns:
            A dict containing:
            - all fields from the per-bottleneck BottleneckValidation model
            - node_id, chunk_id, bottleneck_id metadata
        """
        prompt = self._build_validation_prompt(extracted_text)

        validation = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=self.validation_model,
            system_message=VALIDATION_SYSTEM_PROMPT,
        )

        data = validation.model_dump(mode="json")
        data["node_id"] = node_id
        data["chunk_id"] = chunk_id
        data["bottleneck_id"] = self.bottleneck_id

        return data


    def _build_validation_prompt(self, extracted_text: str) -> str:
        """Build prompt for validating extracted evidence."""
        schema = self.schema
        definition = self.definition

        # Build custom sections from schema (e.g., your big 6.1 block)
        custom_sections = ""
        if schema.get("prompt_sections"):
            for section_name, section_text in schema["prompt_sections"].items():
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
            {self._format_list(schema["strong_cues"])}

            Moderate Cues (need TWO or more):
            {self._format_list(schema["moderate_cues"])}

            Hard Negatives (REJECT if these apply):
            {self._format_list(schema["hard_negatives"])}

            SCOPE LOCK:
            {schema.get("scope_lock", "")}

            ACCEPTANCE RULE: {schema["acceptance_rule"]}
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


def run_validation(schema: str, bottleneck_id: str, overwrite: bool = False):
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

    service = Service(dbutils)
    processor = BottleneckProcessor(bottleneck_id, service)

    results = []
    total = len(has_evidence)

    print(f"Validating {total} extractions for bottleneck {bottleneck_id}...")

    for idx, row in tqdm(has_evidence.iterrows(), total=has_evidence.shape[0]):
        chunk_id = row["chunk_id"]
        node_id = row["node_id"]
        extracted_text = row["extracted_evidence"]

        try:
            row_dict = processor.validate_extraction(extracted_text, node_id, chunk_id)
            results.append(row_dict)
        except Exception as e:
            print(f"  Error validating chunk {chunk_id}: {str(e)}")
            results.append(
                {
                    "node_id": node_id,
                    "chunk_id": chunk_id,
                    "bottleneck_id": bottleneck_id,
                    "is_bottleneck_evidence": False,
                    "is_bottleneck_plus_failure": False,
                    "decision": "irrelevant",  # or "error" if you prefer
                    "rationale": f"Validation error: {str(e)}",
                    "strong_cues": [],
                    "moderate_cues": [],
                    "hard_negative": False,
                    "trigger_spans": [],
                    "subtype": "other",
                    "failure_present": False,
                    "failure_types": [],
                    "failure_spans": [],
                }
            )

    print(f"Completed validation: {total} extractions")

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{validated_results_table}")

    evidence_count = results_df["is_bottleneck_evidence"].sum()
    print(f"Results: {evidence_count}/{len(results_df)} validated as evidence")

