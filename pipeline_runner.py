# Databricks notebook source
# MAGIC %pip install -U "pydantic>=2.4,<3" instructor openai azure-identity sentence-transformers

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

from document_ingestion import run_document_ingestion
from prefilter import run_prefilter
from evidence_extraction import run_extraction
from evidence_validation import run_validation
from evidence_reflection import run_reflection
from evidence_summarization import run_summary_generation
from consts import *

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
BOTTLENECK_ID = '1.1'

# COMMAND ----------

run_extraction(
    spark,
    schema=SCHEMA,
    source_table=CHUNKS_TABLE,
    prefilter_results_table=PREFILTER_RESULTS_TABLE,
    bottleneck_id=BOTTLENECK_ID,
)

# COMMAND ----------

run_validation(
    spark,
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
)

# COMMAND ----------

run_reflection(
    spark,
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
)

# COMMAND ----------

run_summary_generation(
    spark,
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
    source_stage="reflection", # change to "reflection" or "validation" depending on the source data
    doc_metadata_table=DOCS_METADATA_TABLE,
    chunks_table=CHUNKS_TABLE, 
)

