"""
Post Validation / Reflection - Extract additional info and generate stylized summaries
from accepted evidence.

Takes either:
- validated results (is_bottleneck_evidence == True), or
- reflection results (keep_as_evidence == True),

joins to extractions + chunks + doc metadata, and produces:
- structured fields (ExtractedInfo)
- a stand-alone stylized summary for each accepted evidence span.
"""

from typing import Optional, List, Literal
import pandas as pd
from pydantic import BaseModel, Field
from tqdm import tqdm
from pyspark.sql import SparkSession
from service import Service
from bottleneck_definitions import load_bottleneck_definition
from consts import LLM_MODEL


class ExtractedInfo(BaseModel):
    """Additional structured information extracted from validated evidence."""
    country: str = Field(..., description="Country referenced in the extracted evidence.")
    issue_area: Optional[str] = Field(None, description="Main sector or topic affected by the bottleneck.")
    reference_to_policy_or_program: Optional[str] = Field(
        None,
        description="Any specific or general policy referenced in the context of the extracted evidence."
    )
    reference_outcome: Optional[str] = Field(
        None,
        description=(
            "What development or sectoral outcome is affected? "
            "This could include unmet policy goals, reduced service delivery, "
            "poor implementation, or failure to achieve intended change."
        )
    )
    key_constraint: str = Field(..., description="Describe what constraint is being evidenced.")
    observed_consequence: Optional[str] = Field(None, description="Any outcome or effect of the constraint.")
    metric_or_statistic: Optional[str] = Field(None, description="Quantitative detail if present (e.g., a funding gap, percentage).")
    closest_sdg: Optional[str] = Field(None, description="If directly relevant, mention the closest SDG. Leave blank if nothing is directly relevant.")
    closest_sdg_target: Optional[str] = Field(None, description="If directly relevant, mention the closest SDG target. Leave blank if nothing is directly relevant.")


class StylizedSummary(BaseModel):
    """Final stylized summary for reports."""
    summary_text: str = Field(
        ...,
        description=(
            "A short, stylized stand-alone summary suitable for inclusion in a public finance report. "
            "It should be readable in isolation without needing the original document."
        ),
    )


SUMMARY_SYSTEM_MESSAGE = """You are a public finance expert working at a multilateral development bank.

Your task is to extract structured components and generate policy-relevant summaries
of public financial management (PFM) bottlenecks.

Be concise, accurate, and grounded in the source text. Do not invent or infer missing details.
"""


class PostValidationProcessor:
    def __init__(self, bottleneck_id: str, service: Service, model: str = LLM_MODEL):
        self.bottleneck_id = bottleneck_id
        self.service = service
        self.model = model
        self.definition = load_bottleneck_definition(bottleneck_id)
        self.examples = self._get_example_summaries()

    def _get_example_summaries(self) -> List[str]:
        """Return example summaries to guide tone and format."""
        return [
            "Student loan repayment rates in Lesotho and Tanzania: There is an announced policy on loan repayment but in practice repayments are not collected with much effort or consistency, so a larger share of public financing for education goes to post-secondary education than the policy requires.",
            "Liberia: Budget credibility remains weak. Liberia has struggled to implement budgets as planned – aggregate expenditure outturns have significantly deviated from approved budgets, indicating limited credibility.",
            "Albania projected a 17% funding gap against its GBV strategy costs.",
            "In Belgium, cuts in the federal budget had resulted in disparities in the GBV policies issued at the regional level, as well as the reduction of funding of the voluntary sector."
        ]


    def extract_additional_info(
        self,
        extracted_evidence: str,
        extended_context: str,
        metadata: tuple,
    ) -> ExtractedInfo:
        """Extract additional structured info from evidence."""
        prompt = self._build_info_extraction_prompt(
            extracted_evidence, extended_context, metadata
        )

        result: ExtractedInfo = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ExtractedInfo,
            system_message=SUMMARY_SYSTEM_MESSAGE,
        )
        return result

    def generate_stylized_summary(
        self,
        extracted_evidence: str,
        extracted_info: ExtractedInfo,
    ) -> str:
        """Generate final stylized summary from extracted info."""
        prompt = self._build_summary_prompt(extracted_evidence, extracted_info)

        result: StylizedSummary = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=StylizedSummary,
            system_message=SUMMARY_SYSTEM_MESSAGE,
        )
        return result.summary_text


    def _build_info_extraction_prompt(
        self,
        extracted_evidence: str,
        context_text: str,
        metadata: tuple,
    ) -> str:
        """Build prompt for additional info extraction."""
        country, doc_name, region, topic_text = metadata
        example_block = "\n".join(f"- {ex}" for ex in self.examples)

        return f"""You are extracting structured components from PFM evidence.

            Document:
            - Country: {country}
            - Title: {doc_name}
            - Region: {region}
            - Topics: {topic_text}

            Bottleneck:
            **{self.definition['name']}** → {self.definition['description']}

            Extended Definition:
            {self.definition.get('extended_definition') or self.definition['description']}

            ---

            Context from document (surrounding the evidence):
            {context_text}

            Validated evidence for this bottleneck:
            \"\"\"{extracted_evidence}\"\"\"

            ---

            Extract the following structured fields:

            - Country
            - Issue Area (e.g., health, education, fiscal management)
            - Reference to policy or program (if applicable)
            - Reference outcome (what development outcome is affected)
            - Key constraint (what's blocking implementation or delivery)
            - Observed consequence (if mentioned)
            - Metric or statistic (if present)
            - Closest SDG (if directly relevant)
            - Closest SDG target (if directly relevant)

            Only extract what is clearly grounded in the text. Do NOT invent or infer missing details.

            Example summaries for tone guidance (do NOT copy content, only style):
            {example_block}
            """

    def _build_summary_prompt(
        self,
        extracted_evidence: str,
        extracted_info: ExtractedInfo,
    ) -> str:
        """Build prompt for stylized summary generation."""
        example_block = "\n".join(f"- {ex}" for ex in self.examples)

        return f"""Generate a concise, report-style summary of a PFM bottleneck.

                Main content (extracted evidence – must remain grounded in this text):
                \"\"\"{extracted_evidence}\"\"\"

                Match the tone of these examples:
                {example_block}

                ---

                Use the structured information below to generate a clear, concise, stand-alone summary (1–5 sentences).

                The summary should:
                - Mention the **country** (if available)
                - Describe the **constraint** clearly
                - Refer to the **policy or program** (if relevant)
                - Include **consequence or impact** if mentioned
                - Include **quantitative figures** if present
                - Be readable in isolation without needing the original document
                - Do not explicitly mention SDGs unless they are clearly referenced in the evidence
                - Do NOT introduce causal claims or details that are not present in the evidence/context

                Structured info:
                {extracted_info.model_dump_json(indent=2)}
                """


def run_summary_generation(
    spark: SparkSession,
    service: Service,
    schema: str,
    bottleneck_id: str,
    doc_metadata_table: str,
    chunks_table: str,
    source_stage: Literal["validation", "reflection"] = "validation",
    overwrite: bool = False
):
    """
    Generate summaries for accepted evidence and save to table.

    source_stage:
        - "validation" → use ..._validated_results with is_bottleneck_evidence == True
        - "reflection" → use ..._reflection_results with keep_as_evidence == True
    """

    extractions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_extractions"

    if source_stage == "validation":
        decisions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_validated_results"
        output_table = f"bottleneck_{bottleneck_id.replace('.', '_')}_summaries_validation"
    else:
        decisions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_reflection_results"
        output_table = f"bottleneck_{bottleneck_id.replace('.', '_')}_summaries_reflection"

    summary_output_table_exists = spark.catalog.tableExists(f"{schema}.{output_table}")

    if summary_output_table_exists and not overwrite:
        print(f"Skipping summarization for {bottleneck_id} because table {schema}.{output_table} already exists (overwrite=False).")
        return

    # Load decision table
    decisions_df = spark.table(f"{schema}.{decisions_table}").toPandas()

    if decisions_df.empty:
        print(f"No decision rows found in {schema}.{decisions_table}")
        return

    if source_stage == "validation":
        positive = decisions_df[decisions_df["is_bottleneck_evidence"] == True].copy()
    else:
        positive = decisions_df[decisions_df["keep_as_evidence"] == True].copy()

    print(f"Loaded {len(positive)} accepted evidence items from {decisions_table}")

    if positive.empty:
        print("No accepted evidence to summarize")
        return

    extractions_df = (
        spark.table(f"{schema}.{extractions_table}")
        .select("node_id", "chunk_id", "extracted_evidence")
        .toPandas()
    )

    doc_metadata_df = spark.sql(f"""
        SELECT
            node_id,
            cntry_name,
            doc_name,
            admin_rgn_name,
            ent_topic_text
        FROM {schema}.{doc_metadata_table}
    """).toPandas()
    chunks_df = spark.table(f"{schema}.{chunks_table}").toPandas()

    chunks_dict = {
        (row["node_id"], row["chunk_id"]): row["text"]
        for _, row in chunks_df.iterrows()
    }

    def get_extended_context(node_id, chunk_id, n=3):
        """Get surrounding context for a chunk (chunk_id-n ... chunk_id+n)."""
        contexts = []
        for i in range(-n, n + 1):
            text = chunks_dict.get((node_id, chunk_id + i), "")
            if text:
                contexts.append(text)
        return "\n\n".join(contexts)

    def get_metadata(node_id):
        """Get document metadata tuple."""
        try:
            row = doc_metadata_df[doc_metadata_df["node_id"] == node_id].iloc[0]
            return (
                row.get("cntry_name", ""),
                row.get("doc_name", ""),
                row.get("admin_rgn_name", ""),
                row.get("ent_topic_text", ""),
            )
        except (IndexError, KeyError):
            return ("", "", "", "")

    merged = positive.merge(
        extractions_df,
        on=["node_id", "chunk_id"],
        how="left",
        validate="many_to_one",
    )

    processor = PostValidationProcessor(bottleneck_id, service)

    results = []
    total = len(merged)

    print(f"Generating summaries for {total} items...")

    for idx, row in tqdm(merged.iterrows(), total=total):
        row_dict = row.to_dict()
        node_id = row_dict["node_id"]
        chunk_id = row_dict["chunk_id"]
        extracted_evidence = row_dict.get("extracted_evidence") or ""

        if not extracted_evidence:
            continue

        extended_context = get_extended_context(node_id, chunk_id)
        metadata = get_metadata(node_id)

        try:
            extracted_info = processor.extract_additional_info(
                extracted_evidence, extended_context, metadata
            )

            summary = processor.generate_stylized_summary(
                extracted_evidence, extracted_info
            )

            result = {
                "node_id": node_id,
                "chunk_id": chunk_id,
                "bottleneck_id": bottleneck_id,
                "source_stage": source_stage,
                "extracted_evidence": extracted_evidence,
                "extended_context": extended_context,
                "final_summary": summary,
                **extracted_info.model_dump(),
            }
            results.append(result)

        except Exception as e:
            print(f"  Error generating summary for chunk {chunk_id}: {str(e)}")
            results.append(
                {
                    "node_id": node_id,
                    "chunk_id": chunk_id,
                    "bottleneck_id": bottleneck_id,
                    "source_stage": source_stage,
                    "extracted_evidence": extracted_evidence,
                    "extended_context": extended_context,
                    "final_summary": f"Error: {str(e)}",
                    "country": "",
                    "issue_area": None,
                    "reference_to_policy_or_program": None,
                    "reference_outcome": None,
                    "key_constraint": "",
                    "observed_consequence": None,
                    "metric_or_statistic": None,
                    "closest_sdg": None,
                    "closest_sdg_target": None,
                }
            )

    print(f"Completed summary generation: {len(results)} summaries")

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{output_table}")

    print(f"Saved to {schema}.{output_table}")

