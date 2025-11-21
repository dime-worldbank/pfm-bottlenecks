# Databricks notebook source
"""
Post Validation - Extract additional info and generate stylized summaries from validated evidence.
Takes validation results and produces structured fields + stylized (stand-alone) summaries.
"""

from typing import Optional, List
import pandas as pd
from pydantic import BaseModel, Field
from tqdm import tqdm


class ExtractedInfo(BaseModel):
    """Additional structured information extracted from validated evidence."""
    country: str = Field(..., description="Country referenced in the extracted evidence.")
    issue_area: Optional[str] = Field(None, description="Main sector or topic affected by the bottleneck.")
    reference_to_policy_or_program: Optional[str] = Field(None, description="Any specific or general policy referenced in the context of the extracted evidence.")
    reference_outcome: Optional[str] = Field(None, description="What development or sectoral outcome is affected? This could include unmet policy goals, reduced service delivery, poor implementation, or failure to achieve intended change.")
    key_constraint: str = Field(..., description="Describe what constraint is being evidenced.")
    observed_consequence: Optional[str] = Field(None, description="Any outcome or effect of the constraint.")
    metric_or_statistic: Optional[str] = Field(None, description="Quantitative detail if present (e.g., a funding gap, percentage).")
    closest_sdg: Optional[str] = Field(None, description="If directly relevant, mention the closest Sustainable Development Goal (SDG). Leave blank if nothing is directly relevant.")
    closest_sdg_target: Optional[str] = Field(None, description="If directly relevant, mention the closest SDG target. Leave blank if nothing is directly relevant.")


class StylizedSummary(BaseModel):
    """Final stylized summary for reports."""
    summary_text: str = Field(..., description="A short, stylized stand-alone summary suitable for inclusion in a public finance report.")


SUMMARY_SYSTEM_MESSAGE = """You are a public finance expert working at a multilateral development bank.

Your task is to extract structured components and generate policy-relevant summaries of public financial management (PFM) bottlenecks.

Be concise, accurate, and grounded in the source text. Do not invent or infer missing details."""


class PostValidationProcessor:
    """Extract additional info and generate stylized summaries from validated evidence."""

    def __init__(self, bottleneck_id: str, service: Service, model: str = "openai/gpt-4o-mini"):
        self.bottleneck_id = bottleneck_id
        self.service = service
        self.model = model
        self.definition = self._load_definition()
        self.examples = self._get_example_summaries()

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
        metadata: tuple
    ) -> ExtractedInfo:
        """Extract additional structured info from evidence."""
        prompt = self._build_info_extraction_prompt(
            extracted_evidence, extended_context, metadata
        )

        result: ExtractedInfo = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ExtractedInfo,
            system_message=SUMMARY_SYSTEM_MESSAGE
        )
        return result

    def generate_stylized_summary(
        self,
        extracted_evidence: str,
        extracted_info: ExtractedInfo
    ) -> str:
        """Generate final stylized summary from extracted info."""
        prompt = self._build_summary_prompt(extracted_evidence, extracted_info)

        result: StylizedSummary = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=StylizedSummary,
            system_message=SUMMARY_SYSTEM_MESSAGE
        )
        return result.summary_text

    def _build_info_extraction_prompt(
        self,
        extracted_evidence: str,
        context_text: str,
        metadata: tuple
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

        Context from document:
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

        Only extract what is clearly grounded in the text. Do not invent or infer missing details.

        Example summaries for tone guidance:
        {example_block}
        """

    def _build_summary_prompt(
        self,
        extracted_evidence: str,
        extracted_info: ExtractedInfo
    ) -> str:
        """Build prompt for stylized summary generation."""
        example_block = "\n".join(f"- {ex}" for ex in self.examples)

        return f"""Generate a concise, report-style summary of a PFM bottleneck.

    Main content (extracted evidence):
    {extracted_evidence}

    Match the tone of these examples:
    {example_block}

    ---

    Use the structured information below to generate a clear, concise summary (1-5 sentences).

    The summary should:
    - Mention the **country**
    - Describe the **constraint** clearly
    - Refer to the **policy or program** (if relevant)
    - Include **consequence or impact**
    - Mention **quantitative figures** if present
    - Do not add extra commentary unless present in the input
    - Do not explicitly include SDGs unless mentioned in the extracted evidence
    - Do not suggest causal effects not explicitly present

    Extracted info:
    {extracted_info.model_dump_json(indent=2)}
    """


def run_summary_generation(
    spark,
    dbutils,
    schema: str,
    bottleneck_id: str,
    doc_metadata_table: str = "per_pfr_document_data",
    chunks_table: str = "per_pfr_chunks"
):
    """Generate summaries for validated evidence and save to table."""
    from service import Service

    results_table = f"bottleneck_{bottleneck_id.replace('.', '_')}_results"
    summaries_table = f"bottleneck_{bottleneck_id.replace('.', '_')}_summaries"

    # Load validated evidence (only positive results)
    results_df = spark.table(f"{schema}.{results_table}").toPandas()
    positive_evidence = results_df[results_df["is_evidence"] == True]

    print(f"Loaded {len(positive_evidence)} positive evidence items for summarization")

    if len(positive_evidence) == 0:
        print("No positive evidence to summarize")
        return

    # Load document metadata and chunks for context
    doc_metadata_df = spark.table(f"{schema}.{doc_metadata_table}").toPandas()
    chunks_df = spark.table(f"{schema}.{chunks_table}").toPandas()

    # Create lookup dicts
    chunks_dict = {
        (row['node_id'], row['chunk_id']): row['chunk_text']
        for _, row in chunks_df.iterrows()
    }

    def get_extended_context(node_id, chunk_id, n=2):
        """Get surrounding context for a chunk."""
        contexts = []
        for i in range(-n, n + 1):
            text = chunks_dict.get((node_id, chunk_id + i), '')
            if text:
                contexts.append(text)
        return '\n\n'.join(contexts)

    def get_metadata(node_id):
        """Get document metadata tuple."""
        try:
            row = doc_metadata_df[doc_metadata_df['node_id'] == node_id].iloc[0]
            return (
                row.get('cntry_name', ''),
                row.get('doc_name', ''),
                row.get('admin_rgn_name', ''),
                row.get('ent_topic_text', '')
            )
        except (IndexError, KeyError):
            return ('', '', '', '')

    service = Service(dbutils)
    processor = PostValidationProcessor(bottleneck_id, service)

    results = []
    total = len(positive_evidence)

    print(f"Processing {total} evidence items...")

    for idx, row in tqdm(positive_evidence.iterrows(), total=total):
        node_id = row["node_id"]
        chunk_id = row["chunk_id"]
        extracted_evidence = row.get("extracted_span") or ""

        if not extracted_evidence:
            continue

        extended_context = get_extended_context(node_id, chunk_id)
        metadata = get_metadata(node_id)

        try:
            # Step 1: Extract additional info
            extracted_info = processor.extract_additional_info(
                extracted_evidence, extended_context, metadata
            )

            # Step 2: Generate stylized summary
            summary = processor.generate_stylized_summary(
                extracted_evidence, extracted_info
            )

            result = {
                'node_id': node_id,
                'chunk_id': chunk_id,
                'bottleneck_id': bottleneck_id,
                'extracted_evidence': extracted_evidence,
                'extended_context': extended_context,
                'final_summary': summary,
                **extracted_info.model_dump()
            }
            results.append(result)

        except Exception as e:
            print(f"  Error generating summary for chunk {chunk_id}: {str(e)}")
            results.append({
                'node_id': node_id,
                'chunk_id': chunk_id,
                'bottleneck_id': bottleneck_id,
                'extracted_evidence': extracted_evidence,
                'extended_context': extended_context,
                'final_summary': f"Error: {str(e)}",
                'country': '',
                'issue_area': None,
                'reference_to_policy_or_program': None,
                'reference_outcome': None,
                'key_constraint': '',
                'observed_consequence': None,
                'metric_or_statistic': None,
                'closest_sdg': None,
                'closest_sdg_target': None,
            })

    print(f"Completed summary generation: {len(results)} summaries")

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{summaries_table}")

    print(f"Saved to {schema}.{summaries_table}")

