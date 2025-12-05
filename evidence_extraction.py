# Databricks notebook source
# MAGIC %pip install -U "pydantic>=2.4,<3" instructor openai azure-identity sentence-transformers

# COMMAND ----------

# MAGIC %run ./service

# COMMAND ----------

# MAGIC %run ./consts

# COMMAND ----------

# MAGIC %run ./bottleneck_definitions

# COMMAND ----------

"""
Evidence Extractor - Extract potential evidence from prefiltered chunks.
Run once per bottleneck. Results are stable unless source changes.
"""

import pandas as pd
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from tqdm import tqdm

class ConfidenceLevel(str, Enum):
    strong = "strong"
    borderline = "borderline"
    weak = "weak"

class ExtractedEvidence(BaseModel):
    """Extraction output - run once per bottleneck."""

    chunk_id: str = Field(default="", description="Chunk identifier")
    bottleneck_id: str = Field(default="", description="Bottleneck ID")

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
        self.definition = self._load_definition()

    def _load_definition(self) -> dict:
        data = load_bottlenecks()
        challenge_id = int(self.bottleneck_id.split('.')[0])
        challenge = data['challenges'][challenge_id]

        for bn in challenge['bottlenecks']:
            if bn['id'] == self.bottleneck_id:
                return {
                    'id': bn['id'],
                    'name': bn['name'],
                    'description': bn['description'],
                    'extended_definition': bn.get('extended_definition', ''),
                    'challenge_name': challenge['name'],
                    'challenge_description': challenge['description']
                }
        raise ValueError(f"Bottleneck {self.bottleneck_id} not found")

    def extract_chunk(self, chunk_text: str, node_id: str, chunk_id: str) -> ExtractedEvidence:
        prompt = self._build_extraction_prompt(chunk_text)

        result: ExtractedEvidence = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ExtractedEvidence,
            system_message="You are a public finance expert extracting evidence from fiscal diagnostic reports."
        )

        result.node_id = node_id
        result.chunk_id = chunk_id
        result.bottleneck_id = self.bottleneck_id
        return result

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


def run_evidence_extraction(schema: str, source_table: str, prefilter_results_table: str, bottleneck_id: str):
    """Extract evidence from prefiltered chunks and save to table."""

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
            evidence = extractor.extract_chunk(chunk_text, node_id, chunk_id)
            result = evidence.model_dump()
            results.append(result)

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

    extractions_table = f"rpf_bottleneck_{bottleneck_id.replace('.', '_')}_extractions"
    spark_results.write.mode("overwrite").saveAsTable(f"{schema}.{extractions_table}")

    extracted_count = results_df['extracted_evidence'].notna().sum()
    print(f"Saved to {schema}.{extractions_table}")


# COMMAND ----------


