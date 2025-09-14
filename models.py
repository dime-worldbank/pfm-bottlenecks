from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Dict, Annotated

from pydantic import BaseModel, Field, confloat, constr, ConfigDict, model_validator

# ===== IDs =====

class ChallengeID(str, Enum):
    _1 = "1"; _2 = "2"; _3 = "3"; _4 = "4"; _5 = "5"; _6 = "6"; _7 = "7"; _8 = "8"; _9 = "9"


class ChallengeHit(BaseModel):
    challenge_id: ChallengeID
    score: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description = "Score of value between 0 and 1 depicting the confidence in the association of that challenge to the chunk. Reserve the score of 1.0 only for those instances where the evidence is extremely strong"

    )
    evidence_span: constr(min_length=1) = Field(
        ...,
        description=(
            "ONE verbatim quote (≤ ~40 words) copied EXACTLY from the provided chunk that supports the given challenge. Take the largest supporting span."
            "If no such quote exists, the challenge must be omitted from the output."
        ),
    )
    rationale: Optional[constr(min_length=1, max_length=500)] = Field(
        None,
        description="≤2 sentences grounded ONLY in the chunk and the quoted text; no outside knowledge.",
    )

Labels = Annotated[
    List[ChallengeHit],
    Field(min_length=0, max_length=9, description="0..9 unique challenges; sorted by score desc after validation.")
]

class ChallengeLabelSet(BaseModel):
    """
    Multilabel classification result. Empty 'labels' means abstain.
    After validation:
      • duplicates are removed (keep highest score per challenge_id),
      • labels are sorted by score descending,
      • length is capped at ≤ 9.
    """
    model_config = ConfigDict(extra="ignore")  # ignore any stray fields from the LLM
    labels: Labels = Field(default_factory=list)

    @model_validator(mode="after")
    def _dedupe_and_sort(self) -> "ChallengeLabelSet":
        # keep highest-scoring hit per challenge_id
        best: Dict[str, ChallengeHit] = {}
        for h in self.labels:
            cid = h.challenge_id.value if hasattr(h.challenge_id, "value") else str(h.challenge_id)
            prev = best.get(cid)
            if prev is None or float(h.score) > float(prev.score):
                best[cid] = h
        # normalize: sort by score desc
        self.labels = sorted(best.values(), key=lambda x: float(x.score), reverse=True)
        # optional: enforce max length (already hinted by Field, but be explicit after dedupe)
        if len(self.labels) > 9:
            self.labels = self.labels[:9]
        return self

    # convenience helpers (optional)
    def ids(self) -> List[str]:
        return [h.challenge_id.value if hasattr(h.challenge_id, "value") else str(h.challenge_id) for h in self.labels]

    def topk(self, k: int) -> "ChallengeLabelSet":
        return ChallengeLabelSet(labels=self.labels[:k])

class DecisionReason(str, Enum):
    OK = "OK"
    MODEL_ABSTAIN = "MODEL_ABSTAIN"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"

@dataclass
class MultiLabelDecision:
    accepted: bool
    reason: DecisionReason
    accepted_labels: List[ChallengeHit]
    raw_result: ChallengeLabelSet

