"""
Judge Agent - Makes final decision on evidence validity based on advocate and skeptic arguments.
"""

from typing import Optional

try:
    from ..service import Service
    from ..consts import DEFAULT_LLM_MODEL
    from ..bottleneck_definitions import load_bottlenecks
    from ..bottleneck_context import BottleneckContext
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from service import Service
    from consts import DEFAULT_LLM_MODEL
    from bottleneck_definitions import load_bottlenecks
    from bottleneck_context import BottleneckContext
from .models import EvidenceInput, AdvocateArgument, SkepticArgument, JudgeDecision


class JudgeAgent:
    """Agent that judges between advocate and skeptic arguments to make final decision."""
    
    def __init__(self, service: Optional[Service] = None, model: Optional[str] = None):
        self.service = service or Service()
        self.model = model or DEFAULT_LLM_MODEL
        self.bottlenecks = load_bottlenecks()
    
    def get_bottleneck_details(self, bottleneck_id: str) -> dict:
        """Get details for a specific bottleneck."""
        challenge_id = int(bottleneck_id.split('.')[0])
        challenge = self.bottlenecks['challenges'].get(challenge_id)
        
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        for bottleneck in challenge['bottlenecks']:
            if bottleneck['id'] == bottleneck_id:
                return {
                    'id': bottleneck_id,
                    'name': bottleneck['name'],
                    'description': bottleneck['description'],
                    'challenge_name': challenge['name']
                }
        
        raise ValueError(f"Bottleneck {bottleneck_id} not found")
    
    def build_prompt(
        self, 
        evidence: EvidenceInput,
        advocate_arg: AdvocateArgument,
        skeptic_arg: SkepticArgument
    ) -> str:
        """Build the prompt for the judge agent."""
        bottleneck = self.get_bottleneck_details(evidence.bottleneck_id)
        enhanced_context = BottleneckContext.format_context_for_prompt(evidence.bottleneck_id)
        
        # Format advocate points
        advocate_points = "\n".join([
            f"  • {p.point} (strength: {p.strength:.2f})"
            for p in advocate_arg.supporting_points[:5]  # Limit to top 5
        ])
        
        # Format skeptic challenges
        skeptic_challenges = "\n".join([
            f"  • [{c.challenge_type}] {c.description} (severity: {c.severity:.2f})"
            for c in skeptic_arg.challenges[:5]  # Limit to top 5
        ])
        
        return f"""You are an impartial judge evaluating whether evidence supports a specific public finance management bottleneck.

Your role is to:
1. Weigh the advocate's arguments FOR the evidence against the skeptic's arguments AGAINST
2. Make a final accept/reject decision with appropriate confidence
3. Focus on evidence quality and definitional alignment
4. Be balanced - don't automatically side with either position

BOTTLENECK BEING EVALUATED:
ID: {bottleneck['id']}
Name: {bottleneck['name']}
Description: {bottleneck['description']}

{enhanced_context}

ORIGINAL EVIDENCE:
Chunk Text: {evidence.chunk_text}
Evidence Span: "{evidence.evidence_span}"

ADVOCATE'S CASE (arguing FOR acceptance):
Main Claim: {advocate_arg.main_claim}
Confidence: {advocate_arg.overall_confidence:.2f}
Alignment Score: {advocate_arg.alignment_score:.2f}
Specificity Score: {advocate_arg.specificity_score:.2f}

Supporting Points:
{advocate_points}

SKEPTIC'S CASE (arguing AGAINST acceptance):
Primary Concern: {skeptic_arg.primary_concern}
Weakness Score: {skeptic_arg.weakness_score:.2f}
Recommendation: {skeptic_arg.recommendation}
{f"Alternative Interpretation: {skeptic_arg.alternative_interpretation}" if skeptic_arg.alternative_interpretation else ""}

Challenges Raised:
{skeptic_challenges}

DECISION CRITERIA:
Consider these factors in your judgment:

1. EVIDENCE QUALITY:
   - Is the evidence specific and concrete, or vague and generic?
   - Does it directly relate to the bottleneck or require logical leaps?
   - Is there sufficient context to make a confident judgment?

2. ARGUMENT STRENGTH:
   - How compelling is the advocate's case? Are the points well-supported?
   - How serious are the skeptic's concerns? Are they fundamental or minor?
   - Is the alternative interpretation more plausible than the bottleneck?

3. DECISION BIAS:
   - Lean toward ACCEPTANCE if evidence is reasonably strong and skeptic concerns are minor
   - Only REJECT if skeptic raises fundamental flaws or evidence is clearly insufficient
   - Remember: we're at Stage 4 (high precision), but don't want to miss genuine evidence

4. CONFIDENCE CALIBRATION:
   - High confidence (>0.8): Clear case with strong evidence and minor concerns
   - Medium confidence (0.5-0.8): Reasonable evidence with some valid concerns
   - Low confidence (<0.5): Borderline case, decision could go either way

Provide your judgment with:
- decision: 'accept' or 'reject'
- confidence: 0.0-1.0 (your confidence in the decision)
- reasoning: Clear explanation of your decision (2-3 sentences)
- key_factors: List of the most important factors that influenced your decision
- advocate_score: 0.0-1.0 (how convincing the advocate was)
- skeptic_score: 0.0-1.0 (how convincing the skeptic was)

Make a clear decision - avoid fence-sitting. If genuinely uncertain, lean toward the side with stronger arguments."""
    
    def judge(
        self,
        evidence: EvidenceInput,
        advocate_arg: AdvocateArgument,
        skeptic_arg: SkepticArgument
    ) -> JudgeDecision:
        """Make final judgment on the evidence based on both arguments."""
        prompt = self.build_prompt(evidence, advocate_arg, skeptic_arg)
        
        system_message = """You are an impartial judge with expertise in public finance management.
Your role is to make final decisions on evidence validity by weighing competing arguments.
Be decisive but fair, focusing on evidence quality and logical consistency.
Remember: high precision is important, but don't reject evidence unnecessarily."""
        
        result = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=JudgeDecision,
            temperature=0.2,  # Low temperature for consistent decisions
            system_message=system_message
        )
        
        # Set the bottleneck_id
        result.bottleneck_id = evidence.bottleneck_id
        
        # Apply decision adjustments based on scores
        result = self._apply_decision_heuristics(result, advocate_arg, skeptic_arg)
        
        return result
    
    def _apply_decision_heuristics(
        self,
        decision: JudgeDecision,
        advocate_arg: AdvocateArgument,
        skeptic_arg: SkepticArgument
    ) -> JudgeDecision:
        """Apply additional heuristics to ensure balanced decisions."""
        
        # Heuristic 1: If advocate is very strong and skeptic recommendation is not 'reject'
        if (advocate_arg.overall_confidence > 0.85 and 
            advocate_arg.alignment_score > 0.8 and
            skeptic_arg.recommendation != 'reject'):
            # Ensure we don't reject based on minor concerns
            if decision.decision == 'reject' and decision.confidence < 0.7:
                decision.decision = 'accept'
                decision.confidence = max(0.5, decision.confidence - 0.1)
                decision.reasoning += " [Adjusted: Strong advocate case with non-critical skeptic concerns]"
        
        # Heuristic 2: If skeptic identifies fundamental flaws
        if (skeptic_arg.weakness_score > 0.85 and
            skeptic_arg.recommendation == 'reject' and
            len([c for c in skeptic_arg.challenges if c.severity > 0.8]) >= 2):
            # Ensure we reject when there are serious issues
            if decision.decision == 'accept' and decision.confidence < 0.6:
                decision.decision = 'reject'
                decision.confidence = max(0.5, decision.confidence)
                decision.reasoning += " [Adjusted: Multiple severe concerns identified]"
        
        # Heuristic 3: Borderline cases with mixed signals
        if (0.4 <= advocate_arg.overall_confidence <= 0.6 and
            0.4 <= skeptic_arg.weakness_score <= 0.6):
            # For borderline cases, slightly favor acceptance (we're at stage 4)
            if decision.confidence < 0.5:
                decision.confidence = 0.45  # Signal uncertainty
                if skeptic_arg.recommendation == 'accept_with_caution':
                    decision.decision = 'accept'
                    decision.reasoning += " [Borderline case - accepting with caution]"
        
        return decision