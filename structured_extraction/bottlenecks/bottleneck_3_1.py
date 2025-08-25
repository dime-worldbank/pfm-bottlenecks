"""
Bottleneck 3.1: Domestic Revenue Policies Generate Insufficient Resources to Achieve Policy Goals
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from ..core.models import BottleneckBase, ValidationBase, ConfidenceLevel


# Bottleneck Definition
BOTTLENECK_ID = "3.1"
BOTTLENECK_NAME = "Domestic Revenue Policies Generate Insufficient Resources to Achieve Policy Goals Given Fiscal Reality"

CHALLENGE_ID = 3
CHALLENGE_NAME = "Mismatch Between Policy Goals, Capability and Resources"
CHALLENGE_DESCRIPTION = (
    "Assesses whether the scope and ambition of public policies are realistically matched with the institutional "
    "capabilities and fiscal resources available. This includes examining whether domestic revenue, administrative "
    "capacity, and institutional mandates are adequate to deliver on stated goals."
)

ROLE_OF_PUBLIC_FINANCE = "Commitment to Feasible Policy"
ROLE_DESCRIPTION = (
    "Finance ministries and other central agencies play a fundamental coordinating role when it comes to policy decisions, "
    "functioning as a clearing house for various policy proposals across sector institutions, promoting dialogue and consultation "
    "around policy trade-offs, and ultimately linking policy objectives with resource availability, mobilization and use. "
    "This helps build commitment to policy decisions that are made and improves their feasibility and the likelihood that they will be implemented."
)

BOTTLENECK_DESCRIPTION = (
    "In many countries, due to economic structure (e.g., large informal sectors), poor policy design and weak administration "
    "capabilities, governments collect only 10–15% of GDP or less in revenues. This limits their fiscal space and constrains "
    "spending on priority policies aimed at achieving development outcomes. This bottleneck captures domestic revenue policies "
    "that fail to generate sufficient resources to achieve policy goals. These failures limits their fiscal capacity and fiscal "
    "space, constraining spending on priority policies aimed at achieving development outcomes. Studies on the financing gap "
    "for SDG achievement have shown this clearly. "
    "Do **not** classify general references to budget constraints or underfunding **unless** they are linked to the structural "
    "limitations of the revenue system. Be careful to distinguish from 1.1 (leadership inaction), 5.2 (disconnect between budget "
    "and policy), or 6.1 (fragmented funding channels)."
)

# Example evidence for this bottleneck
BOTTLENECK_EXAMPLES = []  # No examples provided in the original code for 3.1


# Extraction Model
class Bottleneck_3_1(BottleneckBase):
    extracted_evidence: Optional[str] = Field(
        None,
        description=(
            "Verbatim excerpt from the text that provides concrete evidence that the country's domestic revenue policies "
            "or systems are structurally insufficient to support its development policy goals. "
            "This may include mention of low tax-to-GDP ratios, reliance on narrow tax bases, inability to mobilize adequate "
            "domestic resources, or systemic administrative limitations in tax collection. "
            "Do not extract general funding gaps, underbudgeting, or aspirational statements unless directly linked to the "
            "limitations of the revenue system. "
            "Use only direct text from the source; do not paraphrase or infer."
        )
    )
    reasoning: Optional[str] = Field(
        None,
        description=(
            "Short explanation of how the extracted text indicates a structural mismatch between revenue capacity and policy ambition. "
            "The reasoning must clearly tie the evidence to revenue system weaknesses rather than general resource constraints "
            "or spending shortfalls."
        )
    )


# Validation Model
class BottleneckValidation_3_1(ValidationBase):
    is_too_general: Optional[bool] = Field(
        None, 
        description="True if the evidence is vague or lacks concrete reference to revenue adequacy or revenue system structure."
    )
    
    only_mentions_funding_gaps: Optional[bool] = Field(
        None, 
        description="True if the statement refers to underfunding or budget constraints without linking them to domestic revenue limitations."
    )
    
    about_expenditure_or_budget_not_revenue: Optional[bool] = Field(
        None, 
        description="True if the chunk focuses on budgeting or spending levels rather than domestic system revenue system, "
                   "i.e., tax base, revenue policy, revenue administration, and collection capabilities"
    )
    
    about_external_financing_not_domestic: Optional[bool] = Field(
        None, 
        description="True if the evidence emphasizes external resources like aid or borrowing instead of domestic revenue."
    )
    
    fits_other_bottleneck: Optional[bool] = Field(
        None, 
        description="True if the content appears more relevant to another bottleneck such as 5.2 (budget-policy disconnect), "
                   "1.1 (commitment), or 6.1 (fragmented funding)."
    )
    
    suggested_bottleneck: Optional[str] = Field(
        None, 
        description="Optional short label for what bottleneck this seems to be about, if not 3.1."
    )
    
    international_example_only: Optional[bool] = Field(
        None, 
        description="True if the evidence refers only to international or generic benchmarks and not the specific country in question."
    )
    
    @classmethod
    def validation_guidance(cls) -> str:
        return """
        Validation Guidance for Bottleneck 3.1 – Domestic Revenue Policies Generate Insufficient Resources to Achieve Policy Goals

        This bottleneck focuses on whether the **policy design or limited administration capabilities of domestic revenue systems** 
        (i.e. covering tax base, revenue policy, revenue administration, or collection capabilities) constrain the government's 
        ability to fund its policy objectives.

        Reject evidence in the following situations:
        - Too vague or abstract — lacks reference to specific revenue constraints.
        - Mentions funding shortages or gaps without linking them to the **domestic revenue system** whether policy design or administration capability.
        - Focuses on spending or budgeting capacity, not features of the revenue system such as tax base, revenue policy, 
          revenue administration and collection capabilities.
        - Centers on external financing, grants, or borrowing, not domestic sources of revenue.
        - Fits better under another bottleneck (e.g., misalignment between budgets and policies, fragmented funding).
        - Refers only to international benchmarks or comparisons without relevance to the specific country in question.

        Valid evidence should:
        - Refer to **low domestic revenue mobilization** (e.g., low tax-to-GDP, narrow base, under performance of revenue collection).
        - Mention factors that **limit domestic revenue collection related to tax base, revenue policy, revenue administration, 
          or collection capabilities**.
        - Highlight misalignment between revenue potential and policy ambition or between revenue potential and revenue collection.
        """


# Optional post-validation override (not typically needed for 3.1)
def post_validation_override(row: Dict) -> Dict:
    """
    Optional post-validation logic for bottleneck 3.1
    Currently uses LLM validation decision directly
    
    Args:
        row: Dictionary containing validation results
        
    Returns:
        Dictionary with matched_groups and should_admit decision
    """
    # Check for red flags
    if (row.get("is_too_general") is True or
        row.get("only_mentions_funding_gaps") is True or
        row.get("about_expenditure_or_budget_not_revenue") is True or
        row.get("about_external_financing_not_domestic") is True or
        row.get("international_example_only") is True):
        return {"matched_groups": [], "should_admit": False}
    
    # If none of the red flags, use the LLM's is_valid decision
    if row.get("is_valid") is True:
        return {"matched_groups": ["Standard validation passed"], "should_admit": True}
    
    return {"matched_groups": [], "should_admit": False}