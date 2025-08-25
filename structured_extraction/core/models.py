"""
Base models and enums for PFM Bottleneck Analysis
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class ConfidenceLevel(str, Enum):
    """Confidence levels for evidence extraction"""
    strong = "strong"
    borderline = "borderline"
    weak = "weak"


class ValidationConfidence(str, Enum):
    """Confidence levels for validation"""
    high = "high"
    medium = "medium"
    low = "low"


class BottleneckBase(BaseModel):
    """Base model for all bottleneck extraction results"""
    
    extracted_evidence: Optional[str] = Field(
        None,
        description="Verbatim excerpt from the text that provides concrete evidence"
    )
    
    reasoning: Optional[str] = Field(
        None,
        description="Short explanation of how the extracted text demonstrates the bottleneck"
    )
    
    confidence: Optional[ConfidenceLevel] = Field(
        None,
        description=(
            "How confidently the extracted evidence supports the bottleneck. "
            "Choose 'strong' if the evidence clearly and directly supports the bottleneck, "
            "'borderline' if it is somewhat relevant but may be open to interpretation, "
            "and 'weak' if the evidence is tenuous, ambiguous, or only indirectly related."
        )
    )


class ValidationBase(BaseModel):
    """Base model for all bottleneck validation results"""
    
    is_valid: bool = Field(
        ...,
        description="True if the extracted evidence strongly supports the bottleneck; False otherwise."
    )
    
    validation_reasoning: Optional[str] = Field(
        None,
        description="Explanation justifying the validation decision."
    )
    
    confidence: Optional[ValidationConfidence] = Field(
        None,
        description="Confidence level that the extracted evidence supports the bottleneck."
    )