"""
Pre-filtering agent to quickly identify potentially relevant chunks
"""
from typing import List, Dict
from ..core.models import PreFilterResult, EvidenceSpan
import config


class PreFilterAgent:
    """
    Fast pre-filtering to reduce chunks from ~5000 to ~250
    High recall, low precision - we don't want to miss anything
    """
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.model = config.LLM_MODEL
        
        # Keywords that suggest PFM relevance
        self.keywords = [
            # Governance
            "government", "ministry", "department", "public", "state",
            "parliament", "cabinet", "official", "authority",
            
            # Finance
            "budget", "expenditure", "revenue", "fiscal", "finance",
            "allocation", "disbursement", "funding", "resources",
            
            # Policy
            "policy", "reform", "implementation", "strategy", "program",
            "initiative", "intervention", "priority", "commitment",
            
            # Problems
            "challenge", "constraint", "bottleneck", "issue", "problem",
            "failure", "inadequate", "insufficient", "weak", "poor",
            "fragmented", "delayed", "lack", "gap"
        ]
    
    def filter_batch(self, chunks: List[Dict]) -> List[EvidenceSpan]:
        """
        Filter a batch of chunks to find potentially relevant ones
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of potentially relevant EvidenceSpans
        """
        relevant_spans = []
        
        for chunk in chunks:
            # Quick keyword check first (very fast)
            if self._quick_check(chunk["text"]):
                # Then LLM check for those that pass
                result = self._detailed_check(chunk)
                if result.is_relevant:
                    # Create evidence spans from relevant parts
                    spans = self._extract_spans(chunk, result)
                    relevant_spans.extend(spans)
        
        return relevant_spans
    
    def _quick_check(self, text: str) -> bool:
        """Quick keyword-based relevance check"""
        text_lower = text.lower()
        keyword_count = sum(1 for kw in self.keywords if kw in text_lower)
        return keyword_count >= 3  # At least 3 keywords
    
    def _detailed_check(self, chunk: Dict) -> PreFilterResult:
        """LLM-based relevance check"""
        prompt = f"""
        Quick assessment: Does this text contain evidence of public finance management challenges, 
        bottlenecks, or implementation issues?
        
        Look for:
        - Government policy implementation problems
        - Resource allocation or budget issues  
        - Coordination or fragmentation problems
        - Leadership or commitment failures
        - Revenue or funding challenges
        
        Text:
        {chunk["text"]}
        
        Be inclusive - if there's ANY potential relevance to public finance challenges, mark as relevant.
        Extract specific spans that contain the relevant evidence.
        """
        
        return self.llm_service.execute(
            prompt=prompt,
            model=self.model,
            response_model=PreFilterResult,
            temperature=0.3  # Some variation okay for pre-filter
        )
    
    def _extract_spans(self, chunk: Dict, result: PreFilterResult) -> List[EvidenceSpan]:
        """Extract relevant spans from chunk"""
        spans = []
        
        if result.relevant_spans:
            # Use LLM-identified spans
            for span_text in result.relevant_spans:
                if len(span_text) >= config.MIN_EVIDENCE_LENGTH:
                    spans.append(EvidenceSpan(
                        text=span_text,
                        chunk_id=chunk["chunk_id"],
                        node_id=chunk["node_id"],
                        metadata={
                            "pre_filter_confidence": result.confidence,
                            "keywords": result.keywords_found
                        }
                    ))
        else:
            # Use whole chunk if no specific spans identified
            spans.append(EvidenceSpan(
                text=chunk["text"],
                chunk_id=chunk["chunk_id"],
                node_id=chunk["node_id"],
                metadata={
                    "pre_filter_confidence": result.confidence,
                    "keywords": result.keywords_found
                }
            ))
        
        return spans