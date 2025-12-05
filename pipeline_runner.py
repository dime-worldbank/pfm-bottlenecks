# Databricks notebook source
# MAGIC %run ./imports

# COMMAND ----------

# Run document ingestion
run_document_ingestion(SCHEMA, DOCS_METADATA_TABLE, CHUNKS_TABLE)


# COMMAND ----------

prefilter_results_table = f"{SCHEMA}.{PREFILTER_RESULTS_TABLE}"

# Check if the results table already exists
if spark.catalog.tableExists(prefilter_results_table):
    print(f"{prefilter_results_table} already exists. Skipping prefilter")
else:
    run_prefilter(
        SCHEMA,
        CHUNKS_TABLE,
        PREFILTER_RESULTS_TABLE,
        threshold=0.55
    )


# COMMAND ----------

BOTTLENECK_ID = '3.1'

# COMMAND ----------

# Run evidence extraction by bottleneck
run_evidence_extraction(
    schema=SCHEMA,
    source_table=CHUNKS_TABLE,
    prefilter_results_table=PREFILTER_RESULTS_TABLE,
    bottleneck_id=BOTTLENECK_ID
)

# COMMAND ----------

# Run validation

run_validation(
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID
)

# COMMAND ----------

# final summary and additional infromation extraction
run_summary_generation(
    schema=SCHEMA,
    bottleneck_id=BOTTLENECK_ID,
    doc_metadata_table=DOCS_METADATA_TABLE,
    chunks_table=CHUNKS_TABLE
)

# COMMAND ----------


