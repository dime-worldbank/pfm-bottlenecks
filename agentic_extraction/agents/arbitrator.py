"""
Evidence arbitrator agent - makes final decisions
"""
from typing import Dict, List, Optional
from datetime import datetime
from ..core.models import (
    EvidenceSpan, ClassificationResult, CausalityResult,
    SpecificityResult, SpecificityLevel, FinalEvidence
)
import config


class EvidenceArbitrator:
    """
    Final decision maker that considers all agent inputs
    Applies quality thresholds and makes accept/reject decisions
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.model = config.LLM_MODEL
    
    def arbitrate(self, 
                 span: EvidenceSpan,
                 classification: ClassificationResult,
                 causality: CausalityResult,
                 context: Optional[str] = None) -> Optional[FinalEvidence]:
        """
        Make final decision on evidence quality and validity
        
        Args:
            span: Original evidence span
            classification: Multi-bottleneck classification results
            causality: Causality validation results
            context: Extended context if available
            
        Returns:
            FinalEvidence if accepted, None if rejected
        """
        # First check if there's a valid classification
        if not classification.top_matches:
            return None  # No bottleneck matches
        
        # Assess specificity
        specificity = self._assess_specificity(span, context)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            classification, causality, specificity
        )
        
        # Make final decision
        is_valid, reasoning = self._make_final_decision(
            classification, causality, specificity, quality_score
        )
        
        if not is_valid:
            return None  # Rejected
        
        # Create final evidence
        return FinalEvidence(
            node_id=span.node_id,
            chunk_id=span.chunk_id,
            text=span.text,
            extended_context=context,
            primary_bottleneck_id=classification.top_matches[0].bottleneck_id,
            primary_confidence=classification.top_matches[0].score,
            alternative_bottlenecks=[
                (match.bottleneck_id, match.score) 
                for match in classification.top_matches[1:]
            ],
            causality=causality,
            specificity=specificity,
            is_valid=is_valid,
            validation_reasoning=reasoning,
            quality_score=quality_score,
            processing_timestamp=datetime.now().isoformat(),
            agent_trace=["pre_filter", "classifier", "causality_validator", "arbitrator"]
        )
    
    def _assess_specificity(self, span: EvidenceSpan, 
                           context: Optional[str]) -> SpecificityResult:
        """Assess the specificity of evidence"""
        
        prompt = f"""
        Assess the specificity of this evidence. Specific evidence includes:
        - Named entities (ministries, departments, programs, people)
        - Dates, timeframes, or periods
        - Quantitative data (amounts, percentages, ratios)
        - Specific policies or reforms mentioned by name
        - Geographic locations
        
        Evidence:
        "{span.text}"
        
        {f"Context: {context}" if context else ""}
        
        Identify:
        1. What specific elements are present?
        2. What's missing that would make this more specific?
        3. Overall specificity level: high/medium/low/insufficient
        
        Generic statements like "the government failed to..." or "resources were inadequate" 
        are LOW specificity unless accompanied by specific details.
        """
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=SpecificityResult,
            temperature=0.1
        )
        
        return result
    
    def _calculate_quality_score(self,
                                classification: ClassificationResult,
                                causality: CausalityResult,
                                specificity: SpecificityResult) -> float:
        """Calculate overall quality score"""
        
        # Component scores
        classification_score = classification.top_matches[0].score if classification.top_matches else 0.0
        
        # Causality score
        if causality.has_causal_claim:
            if causality.is_justified:
                causality_score = 1.0 if causality.causality_type == "stated" else 0.7
            else:
                causality_score = 0.3  # Unjustified causal claims reduce quality
        else:
            causality_score = 0.8  # No causal claims is neutral-positive
        
        # Specificity score
        specificity_score = specificity.score
        
        # Ambiguity penalty
        ambiguity_penalty = 0.2 if classification.is_ambiguous else 0.0
        
        # Weighted average
        quality = (
            classification_score * 0.4 +
            causality_score * 0.3 +
            specificity_score * 0.3 -
            ambiguity_penalty
        )
        
        return max(0.0, min(1.0, quality))
    
    def _make_final_decision(self,
                            classification: ClassificationResult,
                            causality: CausalityResult,
                            specificity: SpecificityResult,
                            quality_score: float) -> tuple[bool, str]:
        """Make final accept/reject decision with reasoning"""
        
        reasons = []
        reject_reasons = []
        
        # Check classification confidence
        top_score = classification.top_matches[0].score
        if top_score < 0.5:
            reject_reasons.append(f"Low classification confidence ({top_score:.2f})")
        elif top_score >= 0.8:
            reasons.append(f"Strong bottleneck match ({top_score:.2f})")
        else:
            reasons.append(f"Moderate bottleneck match ({top_score:.2f})")
        
        # Check causality
        if causality.has_causal_claim and not causality.is_justified:
            reject_reasons.append("Unjustified causal claims")
        elif causality.has_causal_claim and causality.causality_type == "inferred":
            if config.CAUSALITY_STRICTNESS == "high":
                reject_reasons.append("Inferred causality (high strictness mode)")
            else:
                reasons.append("Causal relationship identified (inferred)")
        elif causality.has_causal_claim and causality.is_justified:
            reasons.append("Justified causal relationship")
        
        # Check specificity
        if specificity.specificity_level == SpecificityLevel.INSUFFICIENT:
            reject_reasons.append("Insufficient specificity")
        elif specificity.specificity_level == SpecificityLevel.LOW:
            if quality_score < 0.7:  # Low specificity only acceptable with high other scores
                reject_reasons.append("Too generic without strong other evidence")
        elif specificity.specificity_level == SpecificityLevel.HIGH:
            reasons.append("Highly specific evidence")
        
        # Check ambiguity
        if classification.is_ambiguous:
            if classification.confidence_spread < 0.15:
                reject_reasons.append("Too ambiguous between multiple bottlenecks")
            else:
                reasons.append("Some ambiguity but clear primary match")
        
        # Final decision
        is_valid = len(reject_reasons) == 0 and quality_score >= 0.6
        
        if is_valid:
            reasoning = f"ACCEPTED: {'; '.join(reasons)}. Quality score: {quality_score:.2f}"
        else:
            reasoning = f"REJECTED: {'; '.join(reject_reasons)}. Quality score: {quality_score:.2f}"
        
        return is_valid, reasoning
    
    def explain_decision(self, evidence: FinalEvidence) -> str:
        """Generate detailed explanation of the decision"""
        
        explanation = f"""
        Evidence Assessment for Bottleneck {evidence.primary_bottleneck_id}
        
        Classification:
        - Primary match: {evidence.primary_bottleneck_id} (confidence: {evidence.primary_confidence:.2f})
        - Alternatives: {evidence.alternative_bottlenecks}
        
        Causality Analysis:
        - Has causal claims: {evidence.causality.has_causal_claim}
        - Type: {evidence.causality.causality_type}
        - Justified: {evidence.causality.is_justified}
        - Reasoning: {evidence.causality.validation_reasoning}
        
        Specificity:
        - Level: {evidence.specificity.specificity_level}
        - Score: {evidence.specificity.score:.2f}
        - Specific elements: {evidence.specificity.specific_elements}
        
        Final Decision: {'ACCEPTED' if evidence.is_valid else 'REJECTED'}
        Quality Score: {evidence.quality_score:.2f}
        Reasoning: {evidence.validation_reasoning}
        """
        
        return explanation