# Databricks notebook source
# MAGIC %pip install -U "pydantic>=2.4,<3" instructor openai azure-identity sentence-transformers

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

from pfm_bottlenecks.document_ingestion import run_document_ingestion
from pfm_bottlenecks.prefilter import run_prefilter
from pfm_bottlenecks.evidence_extraction import run_extraction
from pfm_bottlenecks.evidence_validation import run_validation
from pfm_bottlenecks.evidence_reflection import run_reflection
from pfm_bottlenecks.evidence_summarization import run_summary_generation
from pfm_bottlenecks.service import Service
from pfm_bottlenecks.consts import *

# COMMAND ----------

service = Service(dbutils)

# COMMAND ----------

run_document_ingestion(
    spark,
    SCHEMA,
    DOCS_METADATA_TABLE,
    CHUNKS_TABLE,
)

# COMMAND ----------

run_prefilter(
    spark,
    SCHEMA,
    CHUNKS_TABLE,
    PREFILTER_RESULTS_TABLE,
    threshold=0.55
)

# COMMAND ----------

# TODO: put processed bottlenecks in a list & loop over
BOTTLENECK_ID = '5.1'

# COMMAND ----------

run_extraction(
    spark,
    service,
    schema=SCHEMA,
    source_table=CHUNKS_TABLE,
    prefilter_results_table=PREFILTER_RESULTS_TABLE,
    bottleneck_id=BOTTLENECK_ID,
)

# COMMAND ----------

run_validation(
    spark,
    service,
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
)

# COMMAND ----------

run_reflection(
    spark,
    service,
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
)

# COMMAND ----------

run_summary_generation(
    spark,
    service,
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
    source_stage="reflection", # change to "reflection" or "validation" depending on the source data
    doc_metadata_table=DOCS_METADATA_TABLE,
    chunks_table=CHUNKS_TABLE,
)

