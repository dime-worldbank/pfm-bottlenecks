"""
Bottleneck 1.1: Inadequate Commitment of Political and Technical Leadership
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from ..core.models import BottleneckBase, ValidationBase, ConfidenceLevel


# Bottleneck Definition
BOTTLENECK_ID = "1.1"
BOTTLENECK_NAME = "Inadequate Commitment of Political and Technical Leadership"

CHALLENGE_ID = 1
CHALLENGE_NAME = "Insufficient Stakeholder Commitment to Policy Action"
CHALLENGE_DESCRIPTION = (
    "Focuses on whether political and technical stakeholders demonstrate sustained commitment "
    "to implementing approved policies, including challenges around ownership, continuity, and buy-in."
)

ROLE_OF_PUBLIC_FINANCE = "Commitment to Feasible Policy"
ROLE_DESCRIPTION = (
    "Finance ministries and other central agencies play a fundamental coordinating role when it comes to policy decisions, "
    "functioning as a clearing house for various policy proposals across sector institutions, promoting dialogue and consultation "
    "around policy trade-offs, and ultimately linking policy objectives with resource availability, mobilization and use. "
    "This helps build commitment to policy decisions that are made and improves their feasibility and the likelihood that they will be implemented."
)

BOTTLENECK_DESCRIPTION = (
    "This bottleneck applies when there is a clear lack of sustained commitment by political or technical leaders to implement approved policies. "
    "This includes delays, resistance, or failure to act when reforms threaten the status quo, require politically difficult trade-offs, "
    "or demand resource shifts that are not followed through despite stated priorities. "
    "Examples include: approved reforms not being enacted, persistent underfunding of a priority despite commitments, or misalignment between stated goals and actual budget execution. "
    "Do **not** classify general governance weakness, vague statements, or budget/funding gaps **unless** directly tied to political/technical unwillingness or inaction. "
    "Be careful to distinguish from other bottlenecks like 2.1 (coordination failures), 5.2 (disconnect between budgets and policy), or 6.3 (weak execution)."
)

# Example evidence for this bottleneck
BOTTLENECK_EXAMPLES = [
    "Student loan repayment rates in Lesotho and Tanzania: There is an announced policy on loan repayment but in practice repayments are not collected with much effort or consistency, so a larger share of public financing for education goes to post-secondary education than the policy requires.",
    "Liberia: Budget credibility remains weak. Liberia has struggled to implement budgets as planned – aggregate expenditure outturns have significantly deviated from approved budgets, indicating limited credibility. Public spending has been highly volatile (rising sharply during aid-fueled booms and then contracting), undermining a stable counter-cyclical policy.",
    "Political commitment to gender equality: According to a recent survey of 12 developing countries, almost all policy-makers (96%) state that 'schools should promote gender equality' yet at the same time almost half (47%) also believe that 'mothers working is bad for their children'. This demonstrates the often large gap between policy rhetoric and policy commitment regarding whether girls should have the same opportunities as boys.",
]


# Extraction Model
class Bottleneck_1_1(BottleneckBase):
    extracted_evidence: Optional[str] = Field(
        None,
        description=(
            "Verbatim excerpt from the text that provides concrete evidence of political or technical leadership failing to commit to implementing approved policies. "
            "Relevant evidence may include examples of delays, failure to act, resistance to disrupting the status quo, or refusal to reallocate resources despite stated goals. "
            "Mere descriptions of policy ambitions or general intentions are not sufficient. "
            "Focus only on failures of action, follow-through, or resource application. "
            "Use only direct text from the source; do not paraphrase or infer."
        )
    )
    reasoning: Optional[str] = Field(
        None,
        description=(
            "Short explanation of how the extracted text demonstrates weak or absent leadership commitment. "
            "The reasoning must be grounded entirely in the quoted text and explain how inaction, delay, or resistance is evident."
        )
    )


# Validation Model with extensive sub-questions
class BottleneckValidation_1_1(ValidationBase):
    # Reform or policy presence
    mentions_approved_reform: Optional[bool] = Field(
        None,
        description="True only if the text explicitly refers to a specific reform, policy, program, recommendation, or budget measure that has been officially approved, agreed upon, or endorsed by government or leadership."
    )
    
    reform_not_followed_through: Optional[bool] = Field(
        None,
        description="True only if the text states or clearly describes that the approved reform or policy has not been implemented, enacted, or operationalized."
    )
    
    followthrough_failure_attributed_to_leadership: Optional[bool] = Field(
        None,
        description="True only if the failure to act is explicitly linked to political or technical leadership."
    )
    
    # Resistance or interference
    political_resistance_described: Optional[bool] = Field(
        None,
        description="True if the text clearly describes political actors actively resisting, avoiding, or opposing a proposed or ongoing reform."
    )
    
    resistance_due_to_political_cost: Optional[bool] = Field(
        None,
        description="True if the resistance is clearly described as stemming from political cost, disruption of patronage, fear of losing influence, or other vested interests."
    )
    
    interference_in_execution: Optional[bool] = Field(
        None,
        description="True if the text describes political or technical actors interfering with, overriding, or distorting the execution of an approved reform or budgeted action."
    )
    
    interference_is_discretionary: Optional[bool] = Field(
        None,
        description="True only if the interference is described as intentional, discretionary, or politically motivated—not due to weak capacity, technical errors, or administrative bottlenecks."
    )
    
    # Resource prioritization
    failure_to_prioritize_resources: Optional[bool] = Field(
        None,
        description="True if the text explicitly describes leadership or ministry unwillingness or failure to reallocate, constrain, or prioritize resources when tradeoffs are necessary."
    )
    
    # Passive signals
    demoralization_or_abandonment_described: Optional[bool] = Field(
        None,
        description="True if the text describes clear symptoms such as demoralization, disengagement, abandonment of reform, or loss of momentum."
    )
    
    passive_signals_linked_to_leadership: Optional[bool] = Field(
        None,
        description="True only if the above symptoms are explicitly or plausibly linked to disengagement or inaction by named political or technical leadership."
    )
    
    # Top-down failure
    central_decision_harmed_implementation: Optional[bool] = Field(
        None,
        description="True if the text shows that a central or national-level decision (or inaction) undermined subnational or delegated implementation or follow-through."
    )
    
    failure_due_to_top_level_coordination: Optional[bool] = Field(
        None,
        description="True only if the issue is clearly attributed to a failure of leadership coordination, consultation, or direction—not to generic system design problems."
    )
    
    # Strict filters
    actor_named_or_identifiable: Optional[bool] = Field(
        None,
        description="True only if a responsible political or technical actor (e.g., a named ministry, Cabinet, Parliament) is explicitly mentioned or clearly implied in the text."
    )
    
    cause_of_inaction_explicit: Optional[bool] = Field(
        None,
        description="True only if the cause of inaction is clearly described as reluctance, disinterest, avoidance, resistance, or disengagement by leadership."
    )
    
    reform_tied_to_government_commitment: Optional[bool] = Field(
        None,
        description="True if the reform or priority is described as originating from government commitments, statements, or strategies—not just from donor reports, technical plans, or analyst recommendations."
    )
    
    alternative_explanations_ruled_out: Optional[bool] = Field(
        None,
        description="True if the text rules out other plausible causes for inaction—such as technical constraints, funding limitations, or institutional capacity gaps."
    )
    
    uses_conditional_language: Optional[bool] = Field(
        None,
        description="True if the text uses conditional or speculative phrases (e.g., 'should', 'could', 'must', 'may') instead of making clear statements about what has or has not happened."
    )
    
    too_vague_or_generic: Optional[bool] = Field(
        None,
        description="True if the text lacks specific examples, actor mentions, or implementation details and instead offers general complaints or aspirations."
    )
    
    fits_other_bottleneck: Optional[str] = Field(
        None,
        description="If the chunk better supports another bottleneck (e.g., 2.1, 5.2, 5.3, 8.2), indicate which. Leave blank if unsure."
    )
    
    @classmethod
    def validation_guidance(cls) -> str:
        return """
        Validation Guidance for Bottleneck 1.1 – Inadequate Commitment of Political and Technical Leadership
        
        This bottleneck focuses on situations where key decision-makers—political or technical—fail to follow through on approved policy actions due to reluctance, resistance, or lack of sustained commitment.
        
        Reject evidence in the following situations:
        
        - Too general or vague — lacks detail or grounded examples.
        - No clear commitment signal — doesn't indicate resistance, inaction, or avoidance by leadership.
        - Only mentions funding — refers to financial needs without linking to leadership failure.
        - Better fits another bottleneck — for example, issues of coordination, implementation, or resourcing.
        - Describes stakeholder engagement — consultation does not imply lack of commitment.
        - Mentions reform ideas without follow-through — statements of intent without action.
        - Refers only to international examples — must include local context or a directly comparable situation.
        
        Valid evidence should:
        
        - Point to actions not being taken due to lack of political or technical will.
        - Indicate avoidance, delay, or quiet abandonment of policy goals by leadership.
        """


def post_validation_override(row: Dict) -> Dict:
    """
    Deterministic post-validation logic for bottleneck 1.1
    Based on validation sub-questions, determines final admission decision
    
    Args:
        row: Dictionary containing validation results
        
    Returns:
        Dictionary with matched_groups and should_admit decision
    """
    group_matches = []
    
    # Global red-flag overrides: disqualify immediately if any are true
    if (
        row.get("too_vague_or_generic") is True or
        row.get("uses_conditional_language") is True
    ):
        return {"matched_groups": [], "should_admit": False}
    
    # Group 1: Reform Not Followed Through (tightened)
    if (
        row.get("mentions_approved_reform") is True and
        row.get("reform_not_followed_through") is True and
        row.get("followthrough_failure_attributed_to_leadership") is True and
        row.get("actor_named_or_identifiable") is True and
        row.get("cause_of_inaction_explicit") is True and
        row.get("reform_tied_to_government_commitment") is True and
        row.get("alternative_explanations_ruled_out") is True
    ):
        group_matches.append("Group 1: Reform Not Followed Through")
    
    # Group 2: Political Resistance to Reform
    if (
        row.get("mentions_approved_reform") is True and
        row.get("political_resistance_described") is True and
        row.get("resistance_due_to_political_cost") is True and
        row.get("actor_named_or_identifiable") is True
    ):
        group_matches.append("Group 2: Political Resistance")
    
    # Group 3: Interference in Execution
    if (
        row.get("mentions_approved_reform") is True and
        row.get("interference_in_execution") is True and
        row.get("interference_is_discretionary") is True and
        row.get("actor_named_or_identifiable") is True
    ):
        group_matches.append("Group 3: Interference in Execution")
    
    # Group 4: Avoidance of Difficult Tradeoffs (tightened)
    if (
        (
            row.get("mentions_approved_reform") is True or
            row.get("failure_to_prioritize_resources") is True
        ) and
        row.get("followthrough_failure_attributed_to_leadership") is True and
        row.get("actor_named_or_identifiable") is True and
        row.get("cause_of_inaction_explicit") is True and
        row.get("alternative_explanations_ruled_out") is True
    ):
        group_matches.append("Group 4: Failure to Prioritize")
    
    # Group 5: Passive Commitment Failure
    if (
        row.get("demoralization_or_abandonment_described") is True and
        row.get("passive_signals_linked_to_leadership") is True and
        row.get("actor_named_or_identifiable") is True
    ):
        group_matches.append("Group 5: Passive Commitment Failure")
    
    # Group 6: Delegated Abdication
    if (
        row.get("central_decision_harmed_implementation") is True and
        row.get("failure_due_to_top_level_coordination") is True and
        row.get("actor_named_or_identifiable") is True
    ):
        group_matches.append("Group 6: Delegated Leadership Failure")
    
    return {
        "matched_groups": group_matches,
        "should_admit": len(group_matches) > 0
    }