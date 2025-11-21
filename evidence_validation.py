# Databricks notebook source
"""
Bottleneck Processor - Main processing engine for bottleneck evidence extraction and validation.
"""

from typing import List
import pandas as pd
from tqdm import tqdm


class BottleneckProcessor:
    """
    Handles  validation in single pass, with optional reflection step.
    """

    def __init__(
        self, bottleneck_id: str, service: Service, model: str = LLM_MODEL
    ):
        """
        Initialize processor for a specific bottleneck.

        Args:
            bottleneck_id: Bottleneck ID (e.g., "2.1", "6.1")
            service: Service instance for LLM calls
            model: Model name for OpenAI (default: gpt-4o)
        """
        self.bottleneck_id = bottleneck_id
        self.service = service
        self.model = model
        self.schema = get_schema(bottleneck_id)
        self.definition = self._load_definition()

    def _load_definition(self) -> dict:
        """Load bottleneck definition from centralized source"""
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
    ) -> BottleneckEvidence:
        """
        Validate extracted evidence against schema cues and hard negatives.
        """
        prompt = self._build_validation_prompt(extracted_text)

        result: BottleneckEvidence = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=BottleneckEvidence,
            system_message=VALIDATION_SYSTEM_PROMPT,
        )

        result.node_id = node_id
        result.chunk_id = chunk_id
        result.bottleneck_id = self.bottleneck_id
        return result

    def _build_validation_prompt(self, extracted_text: str) -> str:
        """Build prompt for validating extracted evidence"""
        schema = self.schema
        definition = self.definition

        # Build custom sections from schema
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
        ```
        {extracted_text}
        ```

        TASK:
        1. Identify which cues are detected (strong, moderate, hard negatives)
        2. Extract trigger spans (diagnostic phrases) and failure spans (consequences)
        3. Apply acceptance rule to make decision
        4. Provide detailed rationale

        Decision Types:
        - "relevant": Cues met, no hard negatives
        - "relevant_with_failure": Cues met + consequence/failure mentioned
        - "irrelevant": Hard negative detected or no qualifying cues
        - "abstain": Uncertain

        Be conservative. Quote verbatim from the extracted text.
        """

    def run_reflection(
        self, evidence: BottleneckEvidence, chunk_text: str
    ) -> ReflectionDecision:
        """
        Optional reflection step (separate LLM call).
        Reviews: definition + extracted evidence + chunk + validation points.
        Makes final decision on whether everything is "kosher".

        Args:
            evidence: Original BottleneckEvidence from process_chunk
            chunk_text: Original chunk text

        Returns:
            ReflectionDecision with reflection results
        """
        if not evidence.is_evidence:
            # No need to reflect on rejected evidence
            return self._create_passthrough_reflection(evidence)

        prompt = self._build_reflection_prompt(evidence, chunk_text)

        reflection: ReflectionDecision = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ReflectionDecision,
            system_message=self.REFLECTION_SYSTEM_PROMPT,
        )

        # Set identifiers and original decision info
        reflection.chunk_id = evidence.chunk_id
        reflection.bottleneck_id = evidence.bottleneck_id
        reflection.original_is_evidence = evidence.is_evidence
        reflection.original_decision_type = evidence.decision_type
        reflection.original_extracted_span = evidence.extracted_span or ""

        return reflection

    def _build_reflection_prompt(
        self, evidence: BottleneckEvidence, chunk_text: str
    ) -> str:
        """Build reflection prompt for quality control"""
        return f"""You are performing a quality control reflection on a bottleneck evidence decision.

        ORIGINAL DECISION:
        - Bottleneck: {self.bottleneck_id} ({self.definition["name"]})
        - Is Evidence: {evidence.is_evidence}
        - Decision Type: {evidence.decision_type}
        - Extracted Span: {evidence.extracted_span}
        - Strong Cues Detected: {evidence.strong_cues_detected}
        - Moderate Cues Detected: {evidence.moderate_cues_detected}
        - Hard Negatives Detected: {evidence.hard_negatives_detected}
        - Trigger Spans: {evidence.trigger_spans}
        - Failure Spans: {evidence.failure_spans}
        - Original Rationale: {evidence.rationale}

        CHUNK TEXT:
        ```
        {chunk_text}
        ```

        BOTTLENECK DEFINITION:
        {self.definition["description"]}

        EXTENDED DEFINITION:
        {self.definition.get("extended_definition") or "N/A"}

        VALIDATION CRITERIA:
        Strong Cues: {self.schema["strong_cues"]}
        Moderate Cues: {self.schema["moderate_cues"]}
        Hard Negatives: {self.schema["hard_negatives"]}
        Acceptance Rule: {self.schema["acceptance_rule"]}

        TASK:
        Review the original decision carefully. Consider:
        1. Is the extracted span truly evidence of this bottleneck?
        2. Were the cues correctly identified?
        3. Are there any hard negatives that were missed?
        4. Does the decision align with the bottleneck definition?
        5. Is everything "kosher" - does it all make sense together?
        6. Are the trigger spans actually verbatim quotes from the chunk?

        Provide your reflection decision and explain if/why you would change the original decision.
        Set decision_changed=true if you disagree with the original decision.
        """

    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt"""
        return "\n".join(f"  - {item}" for item in items)

    def _create_passthrough_reflection(
        self, evidence: BottleneckEvidence
    ) -> ReflectionDecision:
        """Create reflection that passes through rejected evidence"""
        return ReflectionDecision(
            chunk_id=evidence.chunk_id,
            bottleneck_id=evidence.bottleneck_id,
            original_is_evidence=False,
            original_decision_type=evidence.decision_type,
            original_extracted_span=evidence.extracted_span or "",
            reflection_is_evidence=False,
            reflection_decision_type=evidence.decision_type,
            reflection_rationale="No reflection needed - evidence already rejected",
            decision_changed=False,
            change_explanation=None,
        )


def run_validation(schema: str, bottleneck_id: str):
    """Validate extracted evidence against schema. Overwrites results each run."""
    from service import Service

    extractions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_extractions"
    results_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_results"

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

    for idx, row in tqdm(has_evidence.iterrows(), total = has_evidence.shape[0]):
        chunk_id = row["chunk_id"]
        node_id = row["node_id"]
        extracted_text = row["extracted_evidence"]
        try:
            evidence = processor.validate_extraction(extracted_text, node_id, chunk_id)
            result = evidence.model_dump()
            results.append(result)
        except Exception as e:
            print(f"  Error validating chunk {chunk_id}: {str(e)}")
            results.append(
                {
                    "node_id": row["node_id"],
                    "chunk_id": chunk_id,
                    "bottleneck_id": bottleneck_id,
                    "is_evidence": False,
                    "decision_type": "error",
                    "rationale": f"Validation error: {str(e)}",
                    "confidence": "weak",
                    "extracted_span": None,
                    "trigger_spans": [],
                    "failure_spans": [],
                    "strong_cues_detected": [],
                    "moderate_cues_detected": [],
                    "hard_negatives_detected": [],
                }
            )

    print(f"Completed validation: {total} extractions")

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{results_table}")

    evidence_count = results_df["is_evidence"].sum()
    print(f"Results: {evidence_count}/{len(results_df)} validated as evidence")
    print(f"Saved to {schema}.{results_table} (overwritten)")

