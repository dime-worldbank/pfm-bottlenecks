"""
Evidence Extraction Stage - Extracts specific evidence spans for bottlenecks.
This is Stage 3 of the pipeline, coming after classification and before agentic validation.
"""

from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field

try:
    from .service import Service
    from .consts import DEFAULT_LLM_MODEL
    from .bottleneck_definitions import load_bottlenecks
    from .bottleneck_context import BottleneckContext
except ImportError:
    from service import Service
    from consts import DEFAULT_LLM_MODEL
    from bottleneck_definitions import load_bottlenecks
    from bottleneck_context import BottleneckContext


class ExtractionConfidence(str, Enum):
    """Confidence level for extracted evidence."""
    strong = "strong"
    moderate = "moderate"  
    weak = "weak"


class ExtractedEvidence(BaseModel):
    """Model for extracted evidence from a chunk."""
    bottleneck_id: str = Field(..., description="The bottleneck ID (e.g., '1.1', '3.2')")
    
    evidence_span: str = Field(
        ..., 
        description="Verbatim excerpt from the chunk that provides evidence for the bottleneck. Must be exact text."
    )
    
    confidence: ExtractionConfidence = Field(
        ...,
        description=(
            "Confidence in the extraction: "
            "'strong' if evidence clearly and directly supports the bottleneck, "
            "'moderate' if somewhat relevant but open to interpretation, "
            "'weak' if tenuous or only indirectly related"
        )
    )
    
    reasoning: str = Field(
        ...,
        description="Brief explanation of how the extracted text demonstrates the bottleneck (1-2 sentences)"
    )
    
    span_start: Optional[int] = Field(None, description="Start position of evidence in chunk")
    span_end: Optional[int] = Field(None, description="End position of evidence in chunk")


class MultipleExtractions(BaseModel):
    """Container for multiple evidence extractions from a single chunk."""
    extractions: List[ExtractedEvidence] = Field(
        default_factory=list,
        description="List of extracted evidence spans, can be empty if no evidence found"
    )
    
    def has_evidence(self) -> bool:
        """Check if any evidence was extracted."""
        return len(self.extractions) > 0
    
    def get_strong_evidence(self) -> List[ExtractedEvidence]:
        """Get only strong confidence extractions."""
        return [e for e in self.extractions if e.confidence == ExtractionConfidence.strong]
    
    def get_by_bottleneck(self, bottleneck_id: str) -> Optional[ExtractedEvidence]:
        """Get extraction for specific bottleneck."""
        for e in self.extractions:
            if e.bottleneck_id == bottleneck_id:
                return e
        return None


class EvidenceExtractor:
    """Agent that extracts specific evidence spans for bottlenecks."""
    
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
                    'challenge_description': challenge.get('description', '')
                }
        
        raise ValueError(f"Bottleneck {bottleneck_id} not found")
    
    def build_extraction_prompt(self, chunk_text: str, bottleneck_id: str) -> str:
        """Build prompt for extracting evidence for a specific bottleneck."""
        bottleneck = self.get_bottleneck_details(bottleneck_id)
        context = BottleneckContext.get_context(bottleneck_id)
        enhanced_context = BottleneckContext.format_context_for_prompt(bottleneck_id)
        
        # Get extraction guidance from the context
        extraction_guidance = context.get("extraction_guidance", "Extract specific evidence that directly demonstrates this bottleneck.")
        
        return f"""Extract specific evidence from the text that demonstrates the presence of a public finance management bottleneck.

BOTTLENECK DETAILS:
ID: {bottleneck['id']}
Name: {bottleneck['name']}
Description: {bottleneck['description']}

Challenge Context: {bottleneck['challenge_name']}

{enhanced_context}

EXTRACTION GUIDANCE:
{extraction_guidance}

TEXT TO ANALYZE:
{chunk_text}

TASK:
1. Identify the SINGLE MOST RELEVANT and LONGEST continuous span of text that provides evidence for bottleneck {bottleneck_id}
2. Extract the longest possible verbatim excerpt - prefer comprehensive passages over short phrases
3. The span should be a continuous excerpt (not combining separate parts)
4. Extract ONLY direct quotes from the text - do not paraphrase or summarize
5. Focus on specific, concrete evidence rather than general statements
6. The evidence should directly relate to the bottleneck definition

Provide your extraction with:
- evidence_span: Exact verbatim text from the chunk (as long as possible, continuous)
- confidence: 'strong', 'moderate', or 'weak'
- reasoning: Brief explanation of how this text demonstrates the bottleneck

If no relevant evidence is found, return an empty extraction with empty evidence_span."""
    
    def extract_evidence(
        self, 
        chunk_text: str, 
        bottleneck_id: str
    ) -> Optional[ExtractedEvidence]:
        """Extract evidence for a specific bottleneck from a chunk."""
        prompt = self.build_extraction_prompt(chunk_text, bottleneck_id)
        
        system_message = """You are an expert at extracting specific evidence from text.
Your role is to identify the longest possible verbatim quote that provides concrete evidence for public finance management bottlenecks.
Extract comprehensive passages rather than short phrases - the goal is to capture the full context and all relevant details in a single continuous span.
Be precise - extract exact text from the source, but prefer longer excerpts that tell the complete story."""
        
        result = self.service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ExtractedEvidence,
            temperature=0.1,  # Very low temperature for precise extraction
            system_message=system_message
        )
        
        # Set the bottleneck_id
        result.bottleneck_id = bottleneck_id
        
        # Find span positions if possible
        if result.evidence_span and result.evidence_span in chunk_text:
            result.span_start = chunk_text.find(result.evidence_span)
            result.span_end = result.span_start + len(result.evidence_span)
        
        # Return None if extraction is too weak or no evidence found
        if not result.evidence_span or result.confidence == ExtractionConfidence.weak:
            return None
            
        return result
    
    def extract_multiple(
        self, 
        chunk_text: str, 
        bottleneck_ids: List[str]
    ) -> MultipleExtractions:
        """Extract evidence for multiple bottlenecks from a single chunk."""
        extractions = []
        
        for bottleneck_id in bottleneck_ids:
            evidence = self.extract_evidence(chunk_text, bottleneck_id)
            if evidence:
                extractions.append(evidence)
        
        return MultipleExtractions(extractions=extractions)