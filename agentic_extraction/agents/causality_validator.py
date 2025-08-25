"""
Causality validation agent
"""
from typing import List, Optional
from ..core.models import (
    EvidenceSpan, CausalityResult, CausalityType
)
import config


class CausalityValidator:
    """
    Explicitly validates causal claims in evidence
    Distinguishes between stated causation and inferred causation
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.model = config.LLM_MODEL
        self.causal_indicators = config.CAUSAL_INDICATORS
    
    def validate(self, span: EvidenceSpan, 
                context: Optional[str] = None) -> CausalityResult:
        """
        Validate causal claims in evidence
        
        Args:
            span: Evidence span to validate
            context: Additional context if available
            
        Returns:
            Causality validation result
        """
        # Quick check for causal language
        has_causal_words = self._has_causal_indicators(span.text)
        
        if not has_causal_words:
            # Still check with LLM as causality can be implicit
            return self._validate_implicit_causality(span, context)
        else:
            # Detailed validation of explicit causal claims
            return self._validate_explicit_causality(span, context)
    
    def _has_causal_indicators(self, text: str) -> bool:
        """Quick check for causal language"""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.causal_indicators)
    
    def _validate_explicit_causality(self, span: EvidenceSpan, 
                                    context: Optional[str]) -> CausalityResult:
        """Validate explicit causal claims"""
        
        prompt = f"""
        Analyze the causal claims in this evidence. Be very strict about causality vs correlation.
        
        Evidence:
        "{span.text}"
        
        {f"Additional context: {context}" if context else ""}
        
        Questions to answer:
        
        1. CAUSAL CLAIM IDENTIFICATION
        - What specific causal relationship is being claimed?
        - What is presented as the cause?
        - What is presented as the effect?
        - What causal language is used (because, leads to, results in, etc.)?
        
        2. EVIDENCE FOR CAUSATION
        - Is the causal relationship STATED in the text or INFERRED by you?
        - If stated, quote the exact causal statement
        - What evidence supports this causal link?
        - Is there a clear mechanism explained?
        
        3. ALTERNATIVE EXPLANATIONS
        - Could this be mere correlation?
        - What other factors could explain the relationship?
        - Is the timing/sequence clear?
        
        4. VALIDATION
        - Rate the strength of causal evidence: stated/inferred/ambiguous/none
        - Is the causal claim justified by the evidence provided?
        
        Be skeptical: Most relationships are correlations, not causations.
        Only mark as "stated" if the text explicitly states a causal relationship.
        Only mark as "justified" if there's clear evidence for causation, not just co-occurrence.
        """
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=CausalityResult,
            temperature=0.1  # Low temperature for consistency
        )
        
        # Apply strictness setting
        if config.CAUSALITY_STRICTNESS == "high":
            # In high strictness, inferred causality is not justified
            if result.causality_type == CausalityType.INFERRED:
                result.is_justified = False
                result.validation_reasoning += " [High strictness: Inferred causality rejected]"
        
        return result
    
    def _validate_implicit_causality(self, span: EvidenceSpan,
                                    context: Optional[str]) -> CausalityResult:
        """Check for implicit causal claims even without causal words"""
        
        prompt = f"""
        Check if this evidence makes implicit causal claims without using explicit causal language.
        
        Evidence:
        "{span.text}"
        
        Look for:
        - Implied cause-effect relationships
        - Sequential events presented as connected
        - Attribution of outcomes to actions
        - Blame or credit assignment
        
        Even if no explicit causal words are used, the text might still imply causation.
        Be very careful to distinguish between:
        - Temporal sequence (A then B)
        - Correlation (A and B occur together)  
        - Causation (A causes B)
        
        Only identify causation if it's clearly implied, not just possible.
        """
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=CausalityResult,
            temperature=0.1
        )
        
        # Implicit causality is always marked as inferred
        if result.has_causal_claim and result.causality_type == CausalityType.STATED:
            result.causality_type = CausalityType.INFERRED
            result.validation_reasoning = "Implicit causality detected: " + result.validation_reasoning
        
        return result
    
    def challenge_causality(self, span: EvidenceSpan, 
                           causality_result: CausalityResult) -> List[str]:
        """
        Generate challenges to causal claims
        Used for self-critique
        
        Returns:
            List of challenges/questions about the causal claim
        """
        if not causality_result.has_causal_claim:
            return []
        
        challenges = []
        
        # Standard challenges
        challenges.append(f"Could {causality_result.claimed_effect} have occurred without {causality_result.claimed_cause}?")
        challenges.append(f"Are there examples where {causality_result.claimed_cause} didn't lead to {causality_result.claimed_effect}?")
        challenges.append("Is the timing consistent with a causal relationship?")
        challenges.append("Could both be effects of a common cause?")
        
        # Context-specific challenges
        if causality_result.causality_type == CausalityType.INFERRED:
            challenges.append("What explicit evidence would confirm this causal relationship?")
            challenges.append("Why isn't this stated directly if it's true?")
        
        if causality_result.alternative_explanations:
            for alt in causality_result.alternative_explanations[:2]:
                challenges.append(f"Why isn't '{alt}' the real explanation?")
        
        return challenges