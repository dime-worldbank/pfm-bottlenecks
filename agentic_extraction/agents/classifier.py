"""
Multi-bottleneck classifier agent
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from ..core.models import (
    EvidenceSpan, ClassificationResult, BottleneckScore
)
import config


class MultiBottleneckClassifier:
    """
    Simultaneously evaluates evidence against ALL bottlenecks
    Prevents tunnel vision and ensures correct classification
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.model = config.LLM_MODEL
    
    def classify(self, span: EvidenceSpan, bottlenecks: List[Dict[str, Any]]) -> ClassificationResult:
        """
        Classify evidence span against all bottlenecks simultaneously
        
        Args:
            span: Evidence span to classify
            bottlenecks: List of all bottleneck definitions
            
        Returns:
            Classification result with ranked matches
        """
        # Create comprehensive prompt with all bottlenecks
        prompt = self._create_classification_prompt(span, bottlenecks)
        
        # Get scores for all bottlenecks
        scores = self._get_bottleneck_scores(prompt, bottlenecks)
        
        # Rank and filter
        top_matches = self._rank_matches(scores)
        
        # Analyze ambiguity
        is_ambiguous, confidence_spread = self._analyze_ambiguity(top_matches)
        
        # Make recommendation
        recommendation = self._make_recommendation(top_matches, is_ambiguous)
        
        return ClassificationResult(
            top_matches=top_matches,
            is_ambiguous=is_ambiguous,
            confidence_spread=confidence_spread,
            recommendation=recommendation
        )
    
    def _create_classification_prompt(self, span: EvidenceSpan, bottlenecks: List[Dict]) -> str:
        """Create prompt for multi-bottleneck classification"""
        
        bottleneck_descriptions = "\n\n".join([
            f"**Bottleneck {b['id']}: {b['name']}**\n"
            f"Description: {b['description']}\n"
            f"Examples: {', '.join(b.get('examples', ['No examples provided'])[:2])}"
            for b in bottlenecks
        ])
        
        return f"""
        Analyze this evidence and determine which bottleneck(s) it best supports.
        
        IMPORTANT: 
        - Evidence often seems relevant to multiple bottlenecks
        - You must determine the BEST match, not just any match
        - Consider the SPECIFIC details, not general themes
        - Be skeptical - evidence must CLEARLY support the bottleneck
        
        Evidence to analyze:
        "{span.text}"
        
        Available Bottlenecks:
        {bottleneck_descriptions}
        
        For each bottleneck, provide:
        1. Score (0.0-1.0) - how well the evidence matches
        2. Reasoning - why it does or doesn't match
        3. Specific match points - exact aspects that align
        
        Scoring guidelines:
        - 0.8-1.0: Strong, direct evidence for this specific bottleneck
        - 0.5-0.7: Relevant but could fit other bottlenecks too
        - 0.2-0.4: Tangentially related
        - 0.0-0.1: Not relevant
        
        Be critical - most evidence should score below 0.5 for most bottlenecks.
        """
    
    def _get_bottleneck_scores(self, prompt: str, bottlenecks: List[Dict]) -> List[BottleneckScore]:
        """Get scores for all bottlenecks"""
        
        class MultiBottleneckScores(BaseModel):
            scores: List[BottleneckScore] = Field(
                description="Scores for each bottleneck"
            )
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=MultiBottleneckScores,
            temperature=config.TEMPERATURE
        )
        
        return result.scores
    
    def _rank_matches(self, scores: List[BottleneckScore]) -> List[BottleneckScore]:
        """Rank and filter bottleneck matches"""
        # Sort by score
        sorted_scores = sorted(scores, key=lambda x: x.score, reverse=True)
        
        # Filter by threshold and limit
        filtered = [
            s for s in sorted_scores 
            if s.score >= config.CLASSIFICATION_THRESHOLD
        ][:config.MAX_BOTTLENECKS_PER_EVIDENCE]
        
        return filtered
    
    def _analyze_ambiguity(self, matches: List[BottleneckScore]) -> tuple[bool, float]:
        """Analyze if classification is ambiguous"""
        if len(matches) < 2:
            return False, 1.0 if matches else 0.0
        
        spread = matches[0].score - matches[1].score
        is_ambiguous = spread < 0.2  # If top two are within 0.2
        
        return is_ambiguous, spread
    
    def _make_recommendation(self, matches: List[BottleneckScore], is_ambiguous: bool) -> str:
        """Make recommendation based on classification results"""
        if not matches:
            return "REJECT: No bottleneck matches above threshold"
        
        top_score = matches[0].score
        
        if is_ambiguous:
            return "REVIEW: Multiple bottlenecks with similar scores"
        elif top_score >= 0.8:
            return "ACCEPT: Strong match to specific bottleneck"
        elif top_score >= 0.6:
            return "ACCEPT_WITH_REVIEW: Moderate confidence match"
        else:
            return "REVIEW: Low confidence match"


class ComparativeClassifier:
    """
    Alternative classifier that explicitly compares bottlenecks
    Use when ambiguity is high
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.model = config.LLM_MODEL
    
    def compare_top_matches(self, span: EvidenceSpan, 
                           bottleneck1: Dict, bottleneck2: Dict) -> str:
        """
        Directly compare two bottlenecks for the same evidence
        
        Returns:
            ID of the better matching bottleneck
        """
        prompt = f"""
        You must choose which bottleneck this evidence BETTER supports.
        
        Evidence:
        "{span.text}"
        
        Option A - Bottleneck {bottleneck1['id']}: {bottleneck1['name']}
        {bottleneck1['description']}
        
        Option B - Bottleneck {bottleneck2['id']}: {bottleneck2['name']}  
        {bottleneck2['description']}
        
        Consider:
        1. Which bottleneck's SPECIFIC criteria does the evidence meet?
        2. Which bottleneck's examples are more similar to this evidence?
        3. Is there explicit language that points to one over the other?
        
        Choose A or B and explain why it's a better match.
        """
        
        class ComparisonResult(BaseModel):
            better_match: str = Field(description="'A' or 'B'")
            reasoning: str = Field(description="Why this is the better match")
            key_differentiator: str = Field(description="The main factor that decided it")
        
        result = self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=ComparisonResult,
            temperature=0.1  # Low temperature for consistency
        )
        
        return bottleneck1['id'] if result.better_match == 'A' else bottleneck2['id']