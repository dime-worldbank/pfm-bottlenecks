"""
Bottleneck 6.1: Ad hoc, Political and Fragmented Funding Channels
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from ..core.models import BottleneckBase, ValidationBase, ConfidenceLevel


# Bottleneck Definition
BOTTLENECK_ID = "6.1"
BOTTLENECK_NAME = "Ad hoc, Political and Fragmented Funding Channels"

CHALLENGE_ID = 6
CHALLENGE_NAME = "Unreliable, delayed and fragmented funding for delivery"
CHALLENGE_DESCRIPTION = (
    "Assesses how predictable, timely, and well-coordinated funding flows are, and whether fragmentation "
    "or delays impede delivery."
)

ROLE_OF_PUBLIC_FINANCE = "Effective Resource Mobilization & Distribution"
ROLE_DESCRIPTION = (
    "Governments need to raise and allocate and influence private financial resources in support of the pursuit "
    "of their policy objectives, ensuring both that sufficient resources are available when needed, and that these "
    "are allocated according to needs and cost-effectiveness criteria. How governments do this has important "
    "distributional impacts and can influence public and private behaviour towards achievement of objectives."
)

BOTTLENECK_DESCRIPTION = (
    "Governments and public sector entities often rely on multiple, uncoordinated funding mechanisms—such as general funds, "
    "earmarked revenues, donor funding, and intergovernmental transfers. These mechanisms often lack integration, leading to "
    "volatility, administrative duplication, and fragmented service delivery. Discretionary or politically influenced allocation, "
    "parallel management systems (especially from donors), and poor coordination across agencies or levels of government compound "
    "inefficiencies. Common issues include delays, incomplete disbursements, excessive reporting burdens, and poor alignment of "
    "funding with long-term plans or shared objectives."
)

# Example evidence for this bottleneck
BOTTLENECK_EXAMPLES = []  # No examples provided in the original code for 6.1


# Extraction Model
class Bottleneck_6_1(BottleneckBase):
    extracted_evidence: Optional[str] = Field(
        None,
        description=(
            "Verbatim excerpt from the text that shows financial resources for public service delivery are fragmented, "
            "delayed, diverted, or subject to political influences. "
            "Look for references to disconnected funding channels, bureaucratic bottlenecks, donor-specific procedures, "
            "funding unpredictability, or political interference. "
            "General dissatisfaction without explicit reference to financial flow issues should not be extracted. "
            "Use only direct text from the source; do not paraphrase or infer missing information."
        )
    )
    reasoning: Optional[str] = Field(
        None,
        description=(
            "Brief explanation of how the extracted text shows fragmentation, delay, or diversion of public financial resources. "
            "The reasoning should directly tie the evidence to problems in funding mechanisms or delivery channels."
        )
    )


# Validation Model
class BottleneckValidation_6_1(ValidationBase):
    is_too_general: Optional[bool] = Field(
        None, 
        description="True if the evidence is vague or lacks clear reference to how funding mechanisms impede service delivery."
    )
    
    only_mentions_funding_levels: Optional[bool] = Field(
        None, 
        description="True if the chunk mentions how much funding exists or is needed, without discussing fragmentation, delay, or unpredictability."
    )
    
    no_fragmentation_signal: Optional[bool] = Field(
        None, 
        description="True if the chunk doesn't mention multiple funding channels, parallel systems, or coordination failures."
    )
    
    no_reference_to_donors_or_parallel_systems: Optional[bool] = Field(
        None, 
        description="True if donor-related fragmentation or use of parallel systems is not mentioned when expected."
    )
    
    not_about_funding: Optional[bool] = Field(
        None, 
        description="True if the chunk discusses project execution, governance, or service delivery without reference to funding mechanisms at all."
    )
    
    only_about_volatility_or_variation: Optional[bool] = Field(
        None, 
        description="True if the evidence mentions funding volatility, unpredictability, or variation without showing fragmented/ad hoc channels."
    )
    
    system_issues_without_fragmentation: Optional[bool] = Field(
        None, 
        description="True if the text is about system capacity or PFM weaknesses, but not about fragmentation or multiple funding streams."
    )
    
    donor_dependency_without_fragmentation: Optional[bool] = Field(
        None, 
        description="True if the statement refers to donor reliance but not to fragmentation or parallel structures."
    )
    
    mentions_donor_coordination_but_not_fragmentation: Optional[bool] = Field(
        None, 
        description="True if it refers to donor alignment/policy coordination but lacks details on fragmented or duplicative systems."
    )
    
    refers_to_solution_or_reform_plan: Optional[bool] = Field(
        None, 
        description="True if the text describes a reform or intended solution rather than identifying a problem."
    )
    
    international_example_only: Optional[bool] = Field(
        None, 
        description="True if the example refers to a different country or region and not to the context under analysis."
    )
    
    fits_other_bottleneck: Optional[bool] = Field(
        None, 
        description="True if the evidence seems to be about a different bottleneck (e.g., implementation failure, capacity issues, delays)."
    )
    
    suggested_bottleneck: Optional[str] = Field(
        None, 
        description="Short label of another bottleneck this chunk might better support, if not 6.1."
    )
    
    @classmethod
    def validation_guidance(cls) -> str:
        return """
        Validation Guidance for Bottleneck 6.1 – Ad hoc, Political and Fragmented Funding Channels
        
        This bottleneck focuses on whether **the structure and fragmentation of funding channels** undermines effective 
        service or project delivery. Your task is to assess whether the evidence shows a problem arising from multiple, 
        disconnected, or politically influenced funding streams — particularly if this causes inefficiencies, uncertainty, 
        or administrative burden.
        
        Reject evidence in the following situations:
        
        - Too general or vague — no specific examples of funding systems or fragmentation.
        - Describes volatility or unpredictability of funding, but not fragmentation or structural issues.
        - Refers to shortfalls or underfunding without specifying the fragmented or parallel nature of financing.
        - Discusses unreliability or late disbursements, but not political discretion or multiple funding streams.
        - Focuses on donor dependency without addressing parallel or disconnected systems.
        - Describes weaknesses in systems (e.g., poor controls or procedures) without reference to fragmentation or parallelism.
        - Mentions solutions or reforms already underway, rather than identifying a bottleneck.
        - Cites international experiences without clear relevance to the context being assessed.
        - Addresses coordination failures without linking them to fragmented funding mechanisms.
        
        Valid evidence should describe:
        
        - The presence of **multiple, disconnected, or parallel funding mechanisms** (e.g. budget funds, donor funds, earmarked transfers).
        - Examples of **political discretion** influencing fund allocation or availability.
        - **Administrative inefficiencies or confusion** caused by having multiple reporting or budgeting systems.
        - Specific instances where **fragmentation of funding** made policy planning or implementation difficult.
        """


# Optional post-validation override (not typically needed for 6.1)
def post_validation_override(row: Dict) -> Dict:
    """
    Optional post-validation logic for bottleneck 6.1
    Currently uses LLM validation decision directly
    
    Args:
        row: Dictionary containing validation results
        
    Returns:
        Dictionary with matched_groups and should_admit decision
    """
    # Check for red flags
    if (row.get("is_too_general") is True or
        row.get("only_mentions_funding_levels") is True or
        row.get("no_fragmentation_signal") is True or
        row.get("not_about_funding") is True or
        row.get("refers_to_solution_or_reform_plan") is True or
        row.get("international_example_only") is True):
        return {"matched_groups": [], "should_admit": False}
    
    # If none of the red flags, use the LLM's is_valid decision
    if row.get("is_valid") is True:
        return {"matched_groups": ["Standard validation passed"], "should_admit": True}
    
    return {"matched_groups": [], "should_admit": False}