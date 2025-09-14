"""
Skeptic Agent - Challenges the evidence and points out weaknesses.
"""

from typing import Dict, Optional

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
from .models import EvidenceInput, SkepticArgument, SkepticChallenge


class SkepticAgent:
    """Agent that skeptically evaluates evidence and highlights weaknesses."""
    
    def __init__(self, service: Optional[Service] = None, model: Optional[str] = None):
        self.service = service or Service()
        self.model = model or DEFAULT_LLM_MODEL
        self.bottlenecks = load_bottlenecks()
    
    def get_bottleneck_details(self, bottleneck_id: str) -> Dict:
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
                    'challenge_name': challenge['name'],
                    'challenge_description': challenge['description']
                }
        
        raise ValueError(f"Bottleneck {bottleneck_id} not found")
    
    def build_prompt(self, evidence: EvidenceInput) -> str:
        """Build the prompt for the skeptic agent."""
        bottleneck = self.get_bottleneck_details(evidence.bottleneck_id)
        enhanced_context = BottleneckContext.format_context_for_prompt(evidence.bottleneck_id)
        
        return f"""You are a skeptical analyst tasked with critically evaluating whether evidence truly supports a specific public finance management bottleneck.

Your role is to:
1. Challenge the connection between evidence and bottleneck definition
2. Identify ambiguities, alternative interpretations, and logical gaps
3. Point out what's missing or unclear in the evidence
4. Act in good faith - be critical but fair

BOTTLENECK DETAILS:
ID: {bottleneck['id']}
Name: {bottleneck['name']}
Description: {bottleneck['description']}

Challenge Context: {bottleneck['challenge_name']}
Challenge Description: {bottleneck['challenge_description']}

{enhanced_context}

EVIDENCE TO EVALUATE:
Chunk Text: {evidence.chunk_text}

Specific Evidence Span: "{evidence.evidence_span}"

TASK:
Critically evaluate whether this evidence actually demonstrates bottleneck {bottleneck['id']}. Focus on:

1. Ambiguity - Is the language vague or open to interpretation?
2. Alternative explanations - Could this evidence point to other issues?
3. Missing elements - What key aspects of the bottleneck definition are not addressed?
4. Logical leaps - What assumptions must be made to connect evidence to bottleneck?
5. Context limitations - Is important context missing?

Provide your analysis with:
- primary_concern: Main reason this might not be valid evidence (1-2 sentences)
- challenges: List of specific challenges with type, description, and severity (0.0-1.0)
- alternative_interpretation: Alternative way to interpret this evidence (or null if none)
- weakness_score: Overall weakness of the evidence (0.0-1.0, where 1.0 = very weak)
- recommendation: One of 'reject', 'accept_with_caution', or 'needs_more_context'

Be thorough but fair - provide genuine criticism while acknowledging if evidence has some merit."""
    
    def analyze(self, evidence: EvidenceInput) -> SkepticArgument:
        """Analyze the evidence and build a skeptical critique."""
        prompt = self.build_prompt(evidence)
        
        system_message = """You are a critical analyst who identifies weaknesses and gaps in evidence.
Your role is to skeptically evaluate claims, identify ambiguities, and point out what's missing or unclear.
Be thorough but fair - provide genuine criticism while remaining intellectually honest."""
        
        result = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=SkepticArgument,
            temperature=0.4,  # Slightly higher temp for more critical thinking
            system_message=system_message
        )
        
        # Set the bottleneck_id since it's not in the prompt response
        result.bottleneck_id = evidence.bottleneck_id
        
        return result