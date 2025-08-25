"""
Main script demonstrating how to use the PFM Bottleneck Analysis Pipeline
This should be run in a Databricks notebook environment
"""

# Databricks notebook source
# COMMAND ----------
# Install required packages
# !pip install instructor
# !pip install azure.identity openai
# dbutils.library.restartPython()

# COMMAND ----------
# Imports
import pandas as pd
from time import sleep
from random import sample

# Import pipeline components
from core.services import create_azure_client, AzureOpenAIService
from core.database import DatabaseManager
from core.pipeline import BottleneckPipeline
from utils.excel_export import ExcelExporter
from utils.sampling import SamplingStrategy
import config

# COMMAND ----------
# Initialize services
print("Initializing services...")

# Create Azure OpenAI client
client = create_azure_client(dbutils)

# Initialize service with custom system prompt if needed
service = AzureOpenAIService(client=client)

# Initialize database manager
db_manager = DatabaseManager(spark)

# Initialize pipeline
pipeline = BottleneckPipeline(
    llm_service=service,
    db_manager=db_manager,
    model=config.LLM_MODEL
)

# Initialize utilities
excel_exporter = ExcelExporter()
sampler = SamplingStrategy()

# COMMAND ----------
# Select bottleneck to process
BOTTLENECK_ID = "1.1"  # Change this to process different bottlenecks

print(f"Processing bottleneck {BOTTLENECK_ID}")

# COMMAND ----------
# Option 1: Load chunks from database
# Get filtered documents
df_documents = db_manager.get_filtered_documents(
    countries=config.TARGET_COUNTRIES,
    doc_types=config.DOCUMENT_TYPES
)

# Get chunks for these documents
df_chunks = db_manager.read_chunks(node_ids=df_documents.node_id.tolist())

# Convert to list of dictionaries for processing
chunk_data = [
    {'node_id': row['node_id'], 'chunk_id': row['chunk_id'], 'text': row['text']}
    for _, row in df_chunks.iterrows()
]

print(f"Loaded {len(chunk_data)} chunks for processing")

# COMMAND ----------
# Option 2: Sample chunks for testing
# Uncomment to use sampling for initial testing
# sample_size = 100
# chunk_data = sample(chunk_data, min(sample_size, len(chunk_data)))
# print(f"Using {len(chunk_data)} sampled chunks for testing")

# COMMAND ----------
# Run Stage 1: Extraction
print("\n=== Stage 1: Extraction ===")
df_extracted = pipeline.run_extraction(
    bottleneck_id=BOTTLENECK_ID,
    chunks=chunk_data,
    save_to_db=True
)

print(f"Extracted evidence from {len(df_extracted)} chunks")
print(f"Confidence distribution:")
print(df_extracted['extraction_confidence'].value_counts())

# COMMAND ----------
# Run Stage 2: Validation
print("\n=== Stage 2: Validation ===")
df_validated = pipeline.run_validation(
    bottleneck_id=BOTTLENECK_ID,
    df_extracted=df_extracted,  # Or None to read from DB
    save_to_db=True
)

# Check validation results
if "should_admit" in df_validated.columns:
    valid_count = df_validated["should_admit"].sum()
else:
    valid_count = df_validated["is_valid"].sum()

print(f"Validated {valid_count} chunks as true evidence")
print(f"Validation confidence distribution:")
if 'validation_confidence' in df_validated.columns:
    print(df_validated['validation_confidence'].value_counts())

# COMMAND ----------
# Sample for expert review (if needed)
print("\n=== Sampling for Review ===")
df_for_review = sampler.sample_for_review(
    df_validated[df_validated.get("should_admit", df_validated["is_valid"]) == True],
    max_samples=50,
    strategy="stratified",
    confidence_column="validation_confidence"
)

print(f"Sampled {len(df_for_review)} items for expert review")

# Export for review
review_file = excel_exporter.export_for_review(
    df_for_review,
    bottleneck_id=BOTTLENECK_ID,
    filename=f"bottleneck_{BOTTLENECK_ID}_review_sample.xlsx"
)

print(f"Exported review file: {review_file}")

# COMMAND ----------
# Run Stage 3: Formatting (after expert review if applicable)
print("\n=== Stage 3: Formatting ===")
df_formatted = pipeline.run_formatting(
    bottleneck_id=BOTTLENECK_ID,
    df_validated=df_validated,  # Or None to read from DB
    save_to_db=True
)

print(f"Created {len(df_formatted)} final summaries")

# COMMAND ----------
# Export final results
print("\n=== Exporting Final Results ===")
final_file = excel_exporter.export_for_review(
    df_formatted,
    bottleneck_id=BOTTLENECK_ID,
    filename=f"bottleneck_{BOTTLENECK_ID}_final.xlsx"
)

print(f"Exported final results: {final_file}")

# COMMAND ----------
# Optional: Process multiple bottlenecks
# Uncomment to process all available bottlenecks

# all_results = {}
# for bottleneck_id in config.AVAILABLE_BOTTLENECKS:
#     print(f"\nProcessing bottleneck {bottleneck_id}...")
#     results = pipeline.run_full_pipeline(bottleneck_id, chunk_data)
#     all_results[bottleneck_id] = results["formatting"]
# 
# # Export all results to single file
# multi_file = excel_exporter.export_multi_bottleneck(
#     all_results,
#     filename="all_bottlenecks_final.xlsx"
# )
# print(f"Exported all bottlenecks: {multi_file}")

# COMMAND ----------
# Display sample results
if not df_formatted.empty:
    print("\n=== Sample Final Summaries ===")
    for i, row in df_formatted.head(3).iterrows():
        print(f"\nSummary {i+1}:")
        print(f"Country: {row.get('country', 'N/A')}")
        print(f"Issue Area: {row.get('issue_area', 'N/A')}")
        print(f"Summary: {row.get('final_summary', 'N/A')}")
        print("-" * 50)