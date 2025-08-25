"""
Configuration for Agentic Pipeline
"""

# Model configuration
LLM_MODEL = "gpt-4o"
TEMPERATURE = 0 # Lower temperature for more consistent classification

# Pre-filtering thresholds
PRE_FILTER_THRESHOLD = 0.3  # Low threshold to maintain high recall
PRE_FILTER_BATCH_SIZE = 100

# Classification settings
CLASSIFICATION_THRESHOLD = 0.5  # Minimum score to consider a bottleneck match
MAX_BOTTLENECKS_PER_EVIDENCE = 3  # Return top-3 matches
CLASSIFICATION_BATCH_SIZE = 10

# Causality validation
CAUSALITY_STRICTNESS = "high"  # high/medium/low
CAUSAL_INDICATORS = [
    "because", "due to", "leads to", "causes", "results in",
    "therefore", "consequently", "as a result", "owing to",
    "triggers", "drives", "contributes to", "explains"
]

# Evidence quality thresholds
MIN_SPECIFICITY_SCORE = 0.6
MIN_EVIDENCE_LENGTH = 50  # characters
MAX_EVIDENCE_LENGTH = 1000

# Database configuration
DATABASE_NAME = "prd_mega.sboost4"
AGENTIC_RESULTS_TABLE = "agentic_bottleneck_evidence"

# Processing configuration
RATE_LIMIT_DELAY = 0.5  # Faster since fewer calls
MAX_CONTEXT_CHUNKS = 3  # Chunks to retrieve for context

# Active bottlenecks (None = all)
ACTIVE_BOTTLENECKS = None  # or ["1.1", "2.1", "3.1", "6.1"]