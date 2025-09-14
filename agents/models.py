"""
Data models for the agentic validation stage.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class EvidenceInput(BaseModel):
    """Input to the agentic validation stage from extraction."""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    chunk_text: str = Field(..., description="Full text of the chunk")
    bottleneck_id: str = Field(..., description="ID of the bottleneck (e.g., '1.1', '3.2')")
    evidence_span: str = Field(..., description="Extracted evidence span from the chunk")
    span_start: Optional[int] = Field(None, description="Start position of evidence in chunk")
    span_end: Optional[int] = Field(None, description="End position of evidence in chunk")
    
    @field_validator('bottleneck_id')
    @classmethod
    def validate_bottleneck_id(cls, v: str) -> str:
        parts = v.split('.')
        if len(parts) != 2:
            raise ValueError(f"Invalid bottleneck_id format: {v}. Expected 'X.Y' format")
        challenge_id, bottleneck_num = parts
        if not (1 <= int(challenge_id) <= 9):
            raise ValueError(f"Challenge ID must be between 1-9, got {challenge_id}")
        return v


class ArgumentPoint(BaseModel):
    """A single point in an agent's argument."""
    point: str = Field(..., description="The argument point")
    evidence_reference: Optional[str] = Field(None, description="Specific quote supporting this point")
    strength: float = Field(..., ge=0.0, le=1.0, description="Strength of this point (0-1)")


class AdvocateArgument(BaseModel):
    """Output from the advocate agent."""
    bottleneck_id: Optional[str] = Field(None, description="Bottleneck ID (set after LLM response)")
    main_claim: str = Field(..., description="Primary argument for why this is valid evidence")
    supporting_points: List[ArgumentPoint] = Field(..., description="Supporting arguments")
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="How well evidence aligns with definition")
    specificity_score: float = Field(..., ge=0.0, le=1.0, description="How specific the evidence is")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in the match")


class SkepticChallenge(BaseModel):
    """A challenge raised by the skeptic."""
    challenge_type: str = Field(..., description="Type of challenge (e.g., 'ambiguity', 'alternative_interpretation')")
    description: str = Field(..., description="Description of the challenge")
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity of the issue (0-1)")


class SkepticArgument(BaseModel):
    """Output from the skeptic agent."""
    bottleneck_id: Optional[str] = Field(None, description="Bottleneck ID (set after LLM response)")
    primary_concern: str = Field(..., description="Main reason this might not be valid evidence")
    challenges: List[SkepticChallenge] = Field(..., description="Specific challenges to the evidence")
    alternative_interpretation: Optional[str] = Field(None, description="Alternative way to interpret the evidence")
    weakness_score: float = Field(..., ge=0.0, le=1.0, description="Overall weakness of the evidence (0-1)")
    recommendation: str = Field(..., description="Recommendation: 'reject', 'accept_with_caution', or 'needs_more_context'")


class JudgeDecision(BaseModel):
    """Final decision from the judge agent."""
    bottleneck_id: Optional[str] = Field(None, description="Bottleneck ID (set after LLM response)")
    decision: str = Field(..., description="'accept' or 'reject'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the decision (0-1)")
    reasoning: str = Field(..., description="Explanation of the decision")
    key_factors: List[str] = Field(..., description="Key factors that influenced the decision")
    advocate_score: float = Field(..., ge=0.0, le=1.0, description="How convincing the advocate was")
    skeptic_score: float = Field(..., ge=0.0, le=1.0, description="How convincing the skeptic was")
    
    @field_validator('decision')
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v not in ['accept', 'reject']:
            raise ValueError(f"Decision must be 'accept' or 'reject', got {v}")
        return v


class ValidationResult(BaseModel):
    """Complete result from the agentic validation stage."""
    evidence_input: EvidenceInput
    advocate_argument: AdvocateArgument
    skeptic_argument: SkepticArgument
    judge_decision: JudgeDecision
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    @property
    def is_accepted(self) -> bool:
        return self.judge_decision.decision == 'accept'
    
    @property
    def final_confidence(self) -> float:
        return self.judge_decision.confidence