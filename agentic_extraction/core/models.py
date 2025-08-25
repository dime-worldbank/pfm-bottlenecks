"""
Core models for agentic pipeline
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CausalityType(str, Enum):
    """Types of causality claims"""
    STATED = "stated"  # Explicitly stated in text
    INFERRED = "inferred"  # Model is inferring
    NONE = "none"  # No causal claim
    AMBIGUOUS = "ambiguous"  # Unclear


class SpecificityLevel(str, Enum):
    """Levels of evidence specificity"""
    HIGH = "high"  # Specific names, dates, amounts
    MEDIUM = "medium"  # Some specific details
    LOW = "low"  # Generic statements
    INSUFFICIENT = "insufficient"  # Too vague


@dataclass
class EvidenceSpan:
    """Container for evidence as it moves through agents"""
    text: str
    chunk_id: int
    node_id: str
    context: Optional[str] = None
    bottleneck_scores: Dict[str, float] = None
    causality_assessment: Optional['CausalityResult'] = None
    specificity_score: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.bottleneck_scores is None:
            self.bottleneck_scores = {}
        if self.metadata is None:
            self.metadata = {}


class PreFilterResult(BaseModel):
    """Result from pre-filtering agent"""
    is_relevant: bool = Field(
        description="Whether chunk contains potential PFM evidence"
    )
    confidence: float = Field(
        description="Confidence score (0-1)"
    )
    relevant_spans: List[str] = Field(
        default_factory=list,
        description="Specific spans that seem relevant"
    )
    keywords_found: List[str] = Field(
        default_factory=list,
        description="Policy/finance keywords found"
    )
    reasoning: str = Field(
        description="Brief explanation of relevance"
    )


class BottleneckScore(BaseModel):
    """Score for a single bottleneck"""
    bottleneck_id: str
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    specific_match_points: List[str] = Field(
        default_factory=list,
        description="Specific aspects that match"
    )


class ClassificationResult(BaseModel):
    """Result from multi-bottleneck classifier"""
    top_matches: List[BottleneckScore] = Field(
        description="Top bottleneck matches ranked by score"
    )
    is_ambiguous: bool = Field(
        description="True if multiple bottlenecks have similar scores"
    )
    confidence_spread: float = Field(
        description="Difference between top two scores"
    )
    recommendation: str = Field(
        description="Accept/Reject/Review recommendation"
    )


class CausalityResult(BaseModel):
    """Result from causality validator"""
    has_causal_claim: bool = Field(
        description="Whether evidence makes causal claims"
    )
    causality_type: CausalityType = Field(
        description="Type of causality claim"
    )
    causal_phrases: List[str] = Field(
        default_factory=list,
        description="Specific causal language found"
    )
    claimed_cause: Optional[str] = Field(
        None,
        description="What is claimed as cause"
    )
    claimed_effect: Optional[str] = Field(
        None,
        description="What is claimed as effect"
    )
    is_justified: bool = Field(
        description="Whether causal claim is supported by evidence"
    )
    alternative_explanations: List[str] = Field(
        default_factory=list,
        description="Other possible explanations"
    )
    validation_reasoning: str = Field(
        description="Explanation of causality assessment"
    )


class SpecificityResult(BaseModel):
    """Result from specificity assessment"""
    specificity_level: SpecificityLevel
    score: float = Field(ge=0.0, le=1.0)
    specific_elements: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Specific elements found (names, dates, amounts, etc.)"
    )
    missing_context: List[str] = Field(
        default_factory=list,
        description="What context would make this more specific"
    )


class FinalEvidence(BaseModel):
    """Final validated evidence after all agents"""
    # Source information
    node_id: str
    chunk_id: int
    text: str
    extended_context: Optional[str] = None
    
    # Classification
    primary_bottleneck_id: str
    primary_confidence: float
    alternative_bottlenecks: List[Tuple[str, float]] = Field(
        default_factory=list,
        description="Other possible bottlenecks with scores"
    )
    
    # Validation results
    causality: CausalityResult
    specificity: SpecificityResult
    
    # Final decision
    is_valid: bool
    validation_reasoning: str
    quality_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall quality score"
    )
    
    # Metadata
    processing_timestamp: str
    agent_trace: List[str] = Field(
        default_factory=list,
        description="Agents that processed this evidence"
    )