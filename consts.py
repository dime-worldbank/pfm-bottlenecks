
# LLM
DEFAULT_LLM_MODEL = "openai/gpt-4o-mini"

# Classification thresholds
CHALLENGE_CONFIDENCE_THRESHOLD = 0.60


# consts.py
# Tunables for the bottleneck assignment stage.

# Routing / context
WINDOW_CHARS = 400
SHORTLIST_TOP_K = 3

# Judge gates
ASSIGN_THRESHOLD = 0.65
MIN_MARGIN = 0.12

# Similarity / coherence
SIM_THRESHOLD = 0.42  # useful if you add an extra sim gate later

# Judge weights
W_CLAIM = 0.60
W_SIM = 0.25
W_RISK = 0.15  # subtracted as penalty

# Risk penalties (applied inside judge fuse)
PENALTY_GENERIC = 0.10
PENALTY_CAUSAL = 0.12
PENALTY_RECOMMEND_ONLY = 0.08

# LLM model
DEFAULT_MODEL = "openai/gpt-4o-mini"
