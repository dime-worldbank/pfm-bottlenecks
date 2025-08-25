"""
Configuration settings for PFM Bottleneck Analysis Pipeline
"""

# Model configuration
LLM_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = None
DEFAULT_MAX_TOKENS = None

# Database configuration
DATABASE_NAME = "prd_mega.sboost4"
CHUNKS_TABLE = "per_pfr_chunks"
DOCUMENTS_TABLE = "per_pfr_document_data"
METADATA_TABLE = "prd_corpdata.dm_reference_gold.v_dim_imagebank_document"

# Output paths
EXCEL_OUTPUT_PATH = "/Volumes/prd_mega/sboost4/vboost4/Documents/input/Bottleneck"

# Processing configuration
RATE_LIMIT_DELAY = 1  # seconds between API calls
BATCH_SIZE = 10  # number of chunks to process before delay

# Countries for analysis
TARGET_COUNTRIES = [
    'Ghana', 'Ghana|N/A', 'Pakistan', 'Congo, Democratic Republic of',
    'Kenya', 'Africa|Kenya', 'Tunisia', 'Malawi', 'Uganda', 'Cambodia'
]

# Document types to include
DOCUMENT_TYPES = ['Report', 'Public Expenditure Review']

# Bottleneck IDs available in the system
AVAILABLE_BOTTLENECKS = ["1.1", "2.1", "3.1", "6.1"]