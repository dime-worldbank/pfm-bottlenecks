# Databricks notebook source
import requests
from tqdm import tqdm
import pandas as pd

# COMMAND ----------

# helper function for chunking
splitting_expr = '\r\n\r\n'
def chunk_text_by_chars(text, max_chars=5000):
    chunks = []
    for i in range(0, len(text), max_chars):
        chunk = text[i:i + max_chars].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


# COMMAND ----------

def run_document_ingestion(schema: str, docs_table: str, chunks_table: str):
    """Download PER/PFR documents, chunk them, and save to Databricks tables."""

    full_docs_table = f"{schema}.{docs_table}"
    full_chunks_table = f"{schema}.{chunks_table}"

    # Check if tables already exist
    docs_exist = spark.catalog.tableExists(full_docs_table)
    chunks_exist = spark.catalog.tableExists(full_chunks_table)

    if docs_exist and chunks_exist:
        docs_count = spark.table(full_docs_table).count()
        chunks_count = spark.table(full_chunks_table).count()
        print(f"Tables already exist: {full_docs_table} ({docs_count} docs), {full_chunks_table} ({chunks_count} chunks)")
        return

    # Query for PER/PFR documents
    query = """
    SELECT *
    FROM prd_corpdata.dm_reference_gold.v_dim_imagebank_document
    WHERE (
        (doc_name ILIKE '%Public expenditure review%' OR
        doc_name ILIKE '%Public finance review%') AND
        doc_type_name in ('Report', 'Public Expenditure Review') AND
        doc_name not ILIKE '%Summary%' AND
        doc_name not ILIKE '%Synthesis%' AND
        doc_name not ILIKE '%Presentation%' AND
        doc_name not ILIKE '%Infographic%' AND
        doc_name not ILIKE '%Guidence Note%' AND
        doc_name not ILIKE '%Chapter%' AND
        doc_name not ILIKE '%Module%' AND
        lang_name = 'English' AND
        cntry_name in ('Burkina Faso', 'Cambodia', 'Bangladesh', 'Uganda', 'Kenya',
           'Colombia', 'Paraguay', 'Malawi', 'Congo, Democratic Republic of',
           'Nigeria', 'Ghana|N/A', 'Ghana', 'Mozambique', 'Liberia',
           'Uruguay', 'Pakistan', 'Bhutan', 'Chile', 'Tunisia',
           'Africa|Kenya')
    )
    AND doc_date != 'Disclosed'
    AND disclsr_stat_name = 'Disclosed'
    ORDER BY doc_date DESC
    """

    filtered_df = spark.sql(query).toPandas()
    print(f"Found {len(filtered_df)} PER/PFR documents")

    all_chunks = []
    for i, item in tqdm(filtered_df.iterrows(), total=len(filtered_df), desc="Downloading and chunking"):
        try:
            resp = requests.get(item['ext_text_url'], timeout=30)
            resp.raise_for_status()
            text = resp.text

            node_id = str(item['node_id'])
            chunks = chunk_text_by_chars(text)
            all_chunks.extend([(node_id, chunk_idx, chunk) for chunk_idx, chunk in enumerate(chunks)])
        except Exception as e:
            print(f"Error downloading {item['node_id']}: {e}")
            continue

    chunks_df = pd.DataFrame(all_chunks, columns=['node_id', 'chunk_id', 'text'])
    print(f"Created {len(chunks_df)} chunks from {len(filtered_df)} documents")

    # Save documents table
    if not docs_exist:
        spark.createDataFrame(filtered_df).write.saveAsTable(full_docs_table)
        print(f"Created {full_docs_table} with {len(filtered_df)} documents")

    # Save chunks table
    if not chunks_exist:
        spark.createDataFrame(chunks_df).write.saveAsTable(full_chunks_table)
        print(f"Created {full_chunks_table} with {len(chunks_df)} chunks")

