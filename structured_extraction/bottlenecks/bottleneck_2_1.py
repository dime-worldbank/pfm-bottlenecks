"""
Bottleneck 2.1: Fragmented, Inconsistent and Uncoordinated Policies Across or Within Sectors
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from ..core.models import BottleneckBase, ValidationBase, ConfidenceLevel


# Bottleneck Definition
BOTTLENECK_ID = "2.1"
BOTTLENECK_NAME = "Fragmented, Inconsistent and Uncoordinated Policies Across or Within Sectors"

CHALLENGE_ID = 2
CHALLENGE_NAME = "Incoherence and Fragmentation of Policy"
CHALLENGE_DESCRIPTION = (
    "Examines whether policies across sectors and institutions are aligned and mutually supportive, "
    "or whether they reflect siloed decision-making. This includes failures to coordinate across ministries, "
    "levels of government, or between state and non-state actors. Fragmentation often stems from weak interagency "
    "coordination, unclear mandates, or donor-driven parallel systems, resulting in contradictory or overlapping "
    "policies and reduced policy effectiveness."
)

ROLE_OF_PUBLIC_FINANCE = "Commitment to Feasible Policy"
ROLE_DESCRIPTION = (
    "Finance ministries and other central agencies play a fundamental coordinating role when it comes to policy decisions, "
    "functioning as a clearing house for various policy proposals across sector institutions, promoting dialogue and consultation "
    "around policy trade-offs, and ultimately linking policy objectives with resource availability, mobilization and use. "
    "This helps build commitment to policy decisions that are made and improves their feasibility and the likelihood that they will be implemented."
)

BOTTLENECK_DESCRIPTION = (
    "This bottleneck concerns fragmented or inconsistent policy design across or within sectors. "
    "It applies when policy frameworks fail to consider interdependencies, complementarities, or broader strategic coherence—"
    "resulting in duplicative, misaligned, or conflicting policy actions. Valid examples include overlapping initiatives, "
    "disconnected funding aligned to vertical (not integrated) programs, or incoherent policy directions across ministries "
    "or levels of government. Consequences may include inefficiency, blurred accountability, or undermined outcomes. "
    "Do not include cases focused only on spending duplication, implementation challenges, or vague policy quality concerns "
    "unless clearly linked to poor coordination or incoherent design."
)

# Example evidence for this bottleneck
BOTTLENECK_EXAMPLES = [
    "In Malawi, despite consensus on a national Health Benefits Package, donor funding remains locked into vertical, disease-specific programs, creating duplication and missed synergies.",
    "In Kenya, overlapping youth skills initiatives led to inefficiencies and blurred accountability.",
    "Pakistan's 2019 renewable energy policy was developed in isolation from the national power strategy, resulting in incoherent energy transition planning.",
    "In Ghana, agricultural strategies remain disconnected from climate goals, undermining resilience.",
    "In Liberia, political incentives drive higher education funding despite national commitment to universal basic education."
]


# Extraction Model
class Bottleneck_2_1(BottleneckBase):
    extracted_evidence: Optional[str] = Field(
        None,
        description=(
            "Verbatim excerpt from the text that provides concrete evidence of fragmented, inconsistent, or uncoordinated policy design. "
            "Look for examples of conflicting mandates, duplicative schemes, lack of alignment across sectors or institutions, "
            "or absence of cross-sector coordination mechanisms. "
            "Do not extract vague critiques of policy or general governance weakness without explicit reference to inter-policy "
            "inconsistency or siloed formulation. "
            "Use only direct text from the source; do not paraphrase or infer."
        )
    )
    reasoning: Optional[str] = Field(
        None,
        description=(
            "Brief explanation of how the extracted text illustrates fragmented or uncoordinated policy design. "
            "The reasoning should clarify why the excerpt demonstrates lack of alignment or duplication, "
            "and avoid interpretation beyond the quoted material."
        )
    )


# Validation Model
class BottleneckValidation_2_1(ValidationBase):
    is_too_general: Optional[bool] = Field(
        None, 
        description="True if the evidence is vague or lacks specific examples of fragmented or inconsistent policies."
    )
    
    no_fragmentation_signal: Optional[bool] = Field(
        None, 
        description="True if the chunk does not mention disconnected, disjointed, uncoordinated, fragmented, incoherent, confused, or siloed policy formulation."
    )
    
    only_mentions_policy_quality: Optional[bool] = Field(
        None, 
        description="True if the statement critiques policy quality or feasibility but not inconsistency, incoherence, duplication, or overlap."
    )
    
    about_implementation_not_design: Optional[bool] = Field(
        None, 
        description="True if the evidence focuses on implementation failures, not lack of coordination, incoherence or duplication in policy design."
    )
    
    about_donor_influence_but_not_fragmentation: Optional[bool] = Field(
        None, 
        description="True if the evidence references donor influence or support but not its role in fragmentation or duplication."
    )
    
    fits_other_bottleneck: Optional[bool] = Field(
        None, 
        description="True if the content appears more relevant to another bottleneck."
    )
    
    suggested_bottleneck: Optional[str] = Field(
        None, 
        description="Optional short label for what bottleneck this seems to be about, if not 2.1."
    )
    
    international_example_only: Optional[bool] = Field(
        None, 
        description="True if the evidence refers only to international examples or generic experience, not the specific country in question."
    )
    
    no_consequence_of_fragmentation: Optional[bool] = Field(
        None, 
        description="True if fragmentation is mentioned but without showing any consequence like inefficiency, contradiction, or confusion."
    )
    
    confuses_with_funding_fragmentation: Optional[bool] = Field(
        None, 
        description="True if the issue is about fragmentation in funding mechanisms, not policy design or coordination."
    )
    
    confuses_with_information_fragmentation: Optional[bool] = Field(
        None, 
        description="True if the problem relates to data systems, M&E, or information integration (e.g. bottleneck 9.2), not policy coordination."
    )
    
    too_high_level_or_implied: Optional[bool] = Field(
        None, 
        description="True if the evidence only implies fragmentation indirectly or uses high-level language without a clear example or actor misalignment."
    )
    
    no_actor_misalignment: Optional[bool] = Field(
        None, 
        description="True if the chunk does not describe which actors (ministries, agencies, levels) are uncoordinated or working in silos."
    )
    
    @classmethod
    def validation_guidance(cls) -> str:
        return """
        Validation Guidance for Bottleneck 2.1 – Fragmented, Inconsistent and Uncoordinated Policies

        This bottleneck captures failures in policy coherence across or within sectors — where different policies contradict, 
        overlap, or duplicate efforts due to weak coordination, because policymaking is fragmented across bureaucratic silos, 
        due to management incentives or external donor support. These failures of policy coherence result in policies that are 
        inconsistent and difficult to implement, or in unnecessary duplications and overlaps. 

        Reject evidence in the following situations:
        - Too vague or general — lacks grounded, specific examples.
        - Mentions fragmentation but not its consequences (confusion, contradiction, inefficiency).
        - No reference to actor misalignment (ministries, agencies, levels of government).
        - High-level or implied fragmentation without clear example.
        - Misclassifies funding fragmentation (belongs to bottleneck 6.1).
        - Confuses information/MIS integration (belongs to bottleneck 9.2).
        - Only critiques ambition or quality without showing inconsistency or duplication.
        - Focuses on implementation not policy design.
        - Mentions donor influence but not its role in fragmentation or duplication.
        - Refers only to international examples.

        Valid evidence should:
        - Identify inconsistent, disconnected, or uncoordinated policies.
        - Name or describe which actors or agencies are misaligned or working in silos.
        - Show how fragmentation leads to overlap, inefficiency, confusion, or contradictory action.
        - Highlight structural or institutional sources of fragmentation (e.g., sector silos, donor bypassing).
        """


# Optional post-validation override (not needed for 2.1 based on current code)
def post_validation_override(row: Dict) -> Dict:
    """
    Optional post-validation logic for bottleneck 2.1
    Currently uses LLM validation decision directly
    
    Args:
        row: Dictionary containing validation results
        
    Returns:
        Dictionary with matched_groups and should_admit decision
    """
    # For 2.1, we trust the LLM validation more directly
    # But still check for red flags
    
    if (row.get("is_too_general") is True or
        row.get("no_fragmentation_signal") is True or
        row.get("no_actor_misalignment") is True or
        row.get("international_example_only") is True):
        return {"matched_groups": [], "should_admit": False}
    
    # If none of the red flags, use the LLM's is_valid decision
    if row.get("is_valid") is True:
        return {"matched_groups": ["Standard validation passed"], "should_admit": True}
    
    return {"matched_groups": [], "should_admit": False}