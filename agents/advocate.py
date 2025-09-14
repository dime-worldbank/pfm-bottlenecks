"""
Advocate Agent - Makes the case that evidence strongly supports the bottleneck.
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
from .models import EvidenceInput, AdvocateArgument, ArgumentPoint


class AdvocateAgent:
    """Agent that advocates for the evidence being a strong match for the bottleneck."""
    
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
        """Build the prompt for the advocate agent."""
        bottleneck = self.get_bottleneck_details(evidence.bottleneck_id)
        enhanced_context = BottleneckContext.format_context_for_prompt(evidence.bottleneck_id)
        
        return f"""You are an advocate agent tasked with making the strongest possible case that a piece of evidence supports a specific public finance management bottleneck.

Your role is to:
1. Identify all the ways the evidence aligns with the bottleneck definition
2. Highlight specific language and indicators that support the match
3. Build a compelling argument for why this is strong evidence

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
Build the strongest possible argument that this evidence span demonstrates the presence of bottleneck {bottleneck['id']}. Focus on:

1. Direct alignment with the bottleneck definition
2. Specific keywords, phrases, or indicators in the evidence
3. Contextual clues that strengthen the connection
4. The severity or impact suggested by the evidence

Provide your analysis with:
- main_claim: Primary argument for why this is valid evidence (1-2 sentences)
- supporting_points: List of specific arguments with evidence references and strength scores (0.0-1.0)
- alignment_score: How well the evidence aligns with the definition (0.0-1.0)
- specificity_score: How specific and concrete the evidence is (0.0-1.0)
- overall_confidence: Your overall confidence this is good evidence (0.0-1.0)

Be thorough but honest - make the strongest case possible while staying grounded in the actual evidence."""
    
    def analyze(self, evidence: EvidenceInput) -> AdvocateArgument:
        """Analyze the evidence and build an advocacy argument."""
        prompt = self.build_prompt(evidence)
        
        system_message = """You are an expert analyst specializing in public finance management bottlenecks.
Your role is to advocate for evidence that supports specific bottlenecks, building the strongest possible case while remaining grounded in facts."""
        
        result = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=AdvocateArgument,
            temperature=0.3,
            system_message=system_message
        )
        
        # Set the bottleneck_id since it's not in the prompt response
        result.bottleneck_id = evidence.bottleneck_id
        
        return result