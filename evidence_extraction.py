"""
Evidence Extractor - Extract potential evidence from prefiltered chunks.
Run once per bottleneck. Results are stable unless source changes.
"""

import pandas as pd
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from tqdm import tqdm
from pyspark.sql import SparkSession
from service import Service
from bottleneck_definitions import load_bottleneck_definition
from consts import LLM_MODEL

class ConfidenceLevel(str, Enum):
    strong = "strong"
    borderline = "borderline"
    weak = "weak"

class ExtractedEvidence(BaseModel):
    """Extraction output - run once per bottleneck."""

    extracted_evidence: Optional[str] = Field(
        None,
        description="Verbatim excerpt that may support the bottleneck"
    )
    confidence: ConfidenceLevel = Field(
        ...,
        description="Confidence level"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation of why this excerpt was extracted"
    )

class EvidenceExtractor:
    def __init__(self, bottleneck_id: str, service: Service, model: str = LLM_MODEL):
        self.bottleneck_id = bottleneck_id
        self.service = service
        self.model = model
        self.definition = load_bottleneck_definition(bottleneck_id)

    def extract_chunk(self, chunk_text: str, node_id: str, chunk_id: str) -> ExtractedEvidence:
        prompt = self._build_extraction_prompt(chunk_text)

        evidence: ExtractedEvidence = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ExtractedEvidence,
            system_message="You are a public finance expert extracting evidence from fiscal diagnostic reports."
        )
        evidence_dict = evidence.model_dump()
        evidence_dict["node_id"] = node_id
        evidence_dict["chunk_id"] = chunk_id
        evidence_dict["bottleneck_id"] = self.bottleneck_id

        return evidence_dict

    def _build_extraction_prompt(self, chunk_text: str) -> str:
        definition = self.definition

        return f"""You are analyzing a public finance document to extract evidence for a specific bottleneck.

        BOTTLENECK:
        {definition['name']}

        DESCRIPTION:
        {definition['description']}

        EXTENDED DEFINITION:
        {definition.get('extended_definition') or definition['description']}

        CHALLENGE CONTEXT:
        {definition['challenge_name']} - {definition['challenge_description']}

        TEXT TO ANALYZE:
        {chunk_text}

        TASK:
        - Extract verbatim text that provides evidence for this bottleneck
        - Only extract text that is explicitly present
        - If no clear evidence exists, return null for extracted_evidence
        - Indicate confidence: strong (clear match), borderline (partial/indirect), weak (tenuous)
        - Provide brief reasoning for your extraction

        Do not infer or paraphrase - extract exact quotes only.
        """

def run_extraction(spark: SparkSession, schema: str, source_table: str, prefilter_results_table: str, bottleneck_id: str):
    """Extract evidence from prefiltered chunks and save to table."""

    extractions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_extractions"
    extraction_evidence_exist = spark.catalog.tableExists(f"{schema}.{extractions_table}")

    if extraction_evidence_exist:
        print(f"Skipping evidence extraction for {bottleneck_id} as table {schema}.{extractions_table} already exists")
        return

    passed_chunks_df = spark.sql(f"""
        SELECT c.*
        FROM {schema}.{source_table} c
        JOIN {schema}.{prefilter_results_table} r
          ON c.node_id = r.node_id AND c.chunk_id = r.chunk_id
        WHERE r.prefilter_passed = true
    """).toPandas()

    total = len(passed_chunks_df)
    print(f"Loaded {total} prefiltered chunks")

    if total == 0:
        print("No chunks to extract")
        return

    service = Service(dbutils)
    extractor = EvidenceExtractor(bottleneck_id, service)

    results = []
    for idx, row in tqdm(passed_chunks_df.iterrows(), total=passed_chunks_df.shape[0]):
        chunk_id = row['chunk_id']
        chunk_text = row['text']
        node_id = row['node_id']
        try:
            # Now returns a dict (LLM output + metadata)
            row_dict = extractor.extract_chunk(chunk_text, node_id, chunk_id)
            results.append(row_dict)

        except Exception as e:
            print(f"  Error extracting chunk {chunk_id}: {str(e)}")
            results.append({
                'node_id': node_id,
                'chunk_id': chunk_id,
                'bottleneck_id': bottleneck_id,
                'extracted_evidence': None,
                'confidence': 'weak',
                'reasoning': f"Extraction error: {str(e)}"
            })

    print(f"Completed extraction: {total} chunks")

    results_df = pd.DataFrame(results)
    spark_results = spark.createDataFrame(results_df)
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{extractions_table}")

    extracted_count = results_df['extracted_evidence'].notna().sum()
    print(f"Saved to {schema}.{extractions_table}")
    print(f"Extracted evidence in {extracted_count} chunks")
