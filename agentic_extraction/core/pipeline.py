"""
Main orchestration for agentic pipeline
"""
import pandas as pd
from typing import List, Dict, Optional
from tqdm import tqdm
from time import sleep

from ..agents.pre_filter import PreFilterAgent
from ..agents.classifier import MultiBottleneckClassifier, ComparativeClassifier
from ..agents.causality_validator import CausalityValidator
from ..agents.arbitrator import EvidenceArbitrator
from .bottleneck_registry import BottleneckRegistry
from .models import EvidenceSpan, FinalEvidence
import config


class AgenticPipeline:
    """
    Orchestrates the agent-based bottleneck analysis pipeline
    """
    
    def __init__(self, llm_service, db_manager=None):
        """
        Initialize pipeline with agents
        
        Args:
            llm_service: Azure OpenAI service instance
            db_manager: Optional database manager for persistence
        """
        self.llm_service = llm_service
        self.db_manager = db_manager
        
        # Initialize agents
        self.pre_filter = PreFilterAgent(llm_service)
        self.classifier = MultiBottleneckClassifier(llm_service)
        self.comparative_classifier = ComparativeClassifier(llm_service)
        self.causality_validator = CausalityValidator(llm_service)
        self.arbitrator = EvidenceArbitrator(llm_service)
        
        # Initialize registry
        self.registry = BottleneckRegistry()
        
        # Statistics
        self.stats = {
            "total_chunks": 0,
            "pre_filtered_spans": 0,
            "classified_spans": 0,
            "accepted_evidence": 0,
            "rejected_evidence": 0
        }
    
    def analyze(self, 
               chunks: List[Dict],
               bottlenecks: Optional[List[str]] = None,
               min_confidence: float = 0.6,
               save_to_db: bool = True) -> List[FinalEvidence]:
        """
        Run the complete agentic analysis pipeline
        
        Args:
            chunks: List of document chunks to analyze
            bottlenecks: List of bottleneck IDs to check (None = all)
            min_confidence: Minimum confidence threshold
            save_to_db: Whether to save results to database
            
        Returns:
            List of validated evidence
        """
        print(f"Starting agentic analysis of {len(chunks)} chunks")
        self.stats["total_chunks"] = len(chunks)
        
        # Get active bottlenecks
        active_bottlenecks = self.registry.get_active_bottlenecks(bottlenecks)
        print(f"Checking against {len(active_bottlenecks)} bottlenecks")
        
        # Stage 1: Pre-filtering
        print("\n=== Stage 1: Pre-filtering ===")
        relevant_spans = self._pre_filter_chunks(chunks)
        print(f"Pre-filtered to {len(relevant_spans)} relevant spans")
        self.stats["pre_filtered_spans"] = len(relevant_spans)
        
        if not relevant_spans:
            print("No relevant spans found")
            return []
        
        # Stage 2: Multi-bottleneck classification
        print("\n=== Stage 2: Classification ===")
        classified_spans = self._classify_spans(relevant_spans, active_bottlenecks)
        print(f"Classified {len(classified_spans)} spans with bottleneck matches")
        self.stats["classified_spans"] = len(classified_spans)
        
        # Stage 3: Validation and arbitration
        print("\n=== Stage 3: Validation & Arbitration ===")
        final_evidence = self._validate_and_arbitrate(classified_spans, min_confidence)
        print(f"Accepted {len(final_evidence)} final evidence items")
        self.stats["accepted_evidence"] = len(final_evidence)
        self.stats["rejected_evidence"] = len(classified_spans) - len(final_evidence)
        
        # Save to database if requested
        if save_to_db and self.db_manager and final_evidence:
            self._save_results(final_evidence)
        
        # Print summary statistics
        self._print_summary()
        
        return final_evidence
    
    def _pre_filter_chunks(self, chunks: List[Dict]) -> List[EvidenceSpan]:
        """Stage 1: Pre-filter chunks for relevance"""
        relevant_spans = []
        
        # Process in batches for efficiency
        batch_size = config.PRE_FILTER_BATCH_SIZE
        for i in tqdm(range(0, len(chunks), batch_size), desc="Pre-filtering"):
            batch = chunks[i:i + batch_size]
            batch_spans = self.pre_filter.filter_batch(batch)
            relevant_spans.extend(batch_spans)
            
            # Rate limiting
            if i % (batch_size * 10) == 0 and i > 0:
                sleep(config.RATE_LIMIT_DELAY)
        
        return relevant_spans
    
    def _classify_spans(self, spans: List[EvidenceSpan], 
                       bottlenecks: List[Dict]) -> List[Dict]:
        """Stage 2: Classify spans against all bottlenecks"""
        classified_spans = []
        
        for span in tqdm(spans, desc="Classifying"):
            # Classify against all bottlenecks
            classification = self.classifier.classify(span, bottlenecks)
            
            # Only keep spans with matches
            if classification.top_matches:
                # Handle ambiguous cases with comparative classification
                if classification.is_ambiguous and len(classification.top_matches) >= 2:
                    top_two = classification.top_matches[:2]
                    bottleneck1 = self.registry.get_bottleneck(top_two[0].bottleneck_id)
                    bottleneck2 = self.registry.get_bottleneck(top_two[1].bottleneck_id)
                    
                    # Use comparative classifier to resolve
                    better_match = self.comparative_classifier.compare_top_matches(
                        span, bottleneck1, bottleneck2
                    )
                    
                    # Update classification to prefer the better match
                    if better_match == top_two[1].bottleneck_id:
                        classification.top_matches[0], classification.top_matches[1] = \
                            classification.top_matches[1], classification.top_matches[0]
                
                classified_spans.append({
                    "span": span,
                    "classification": classification
                })
            
            # Rate limiting
            if len(classified_spans) % 10 == 0:
                sleep(config.RATE_LIMIT_DELAY)
        
        return classified_spans
    
    def _validate_and_arbitrate(self, classified_spans: List[Dict],
                               min_confidence: float) -> List[FinalEvidence]:
        """Stage 3: Validate causality and make final decisions"""
        final_evidence = []
        
        for item in tqdm(classified_spans, desc="Validating"):
            span = item["span"]
            classification = item["classification"]
            
            # Skip if below minimum confidence
            if classification.top_matches[0].score < min_confidence:
                continue
            
            # Get extended context if available
            context = self._get_context(span) if self.db_manager else None
            
            # Validate causality
            causality = self.causality_validator.validate(span, context)
            
            # Challenge causality if needed
            if causality.has_causal_claim and not causality.is_justified:
                challenges = self.causality_validator.challenge_causality(span, causality)
                # Could use challenges for additional validation here
            
            # Final arbitration
            evidence = self.arbitrator.arbitrate(
                span, classification, causality, context
            )
            
            if evidence:
                final_evidence.append(evidence)
        
        return final_evidence
    
    def _get_context(self, span: EvidenceSpan) -> Optional[str]:
        """Retrieve extended context for a span"""
        if not self.db_manager:
            return None
        
        try:
            # Get surrounding chunks
            chunks_df = self.db_manager.read_chunks(node_ids=[span.node_id])
            
            # Get chunks before and after
            target_chunk_id = span.chunk_id
            context_ids = list(range(
                max(0, target_chunk_id - config.MAX_CONTEXT_CHUNKS),
                target_chunk_id + config.MAX_CONTEXT_CHUNKS + 1
            ))
            
            context_chunks = chunks_df[
                chunks_df.chunk_id.isin(context_ids)
            ].sort_values('chunk_id')
            
            return '\n\n'.join(context_chunks.text.values)
        except:
            return None
    
    def _save_results(self, evidence_list: List[FinalEvidence]):
        """Save results to database"""
        if not self.db_manager:
            return
        
        # Convert to DataFrame
        records = []
        for evidence in evidence_list:
            records.append({
                "node_id": evidence.node_id,
                "chunk_id": evidence.chunk_id,
                "text": evidence.text,
                "bottleneck_id": evidence.primary_bottleneck_id,
                "confidence": evidence.primary_confidence,
                "alternatives": str(evidence.alternative_bottlenecks),
                "has_causal_claim": evidence.causality.has_causal_claim,
                "causality_type": evidence.causality.causality_type,
                "causality_justified": evidence.causality.is_justified,
                "specificity_level": evidence.specificity.specificity_level,
                "specificity_score": evidence.specificity.score,
                "quality_score": evidence.quality_score,
                "is_valid": evidence.is_valid,
                "validation_reasoning": evidence.validation_reasoning,
                "timestamp": evidence.processing_timestamp
            })
        
        df = pd.DataFrame(records)
        
        # Save to database
        self.db_manager._write_to_table(df, config.AGENTIC_RESULTS_TABLE)
        print(f"Saved {len(df)} results to database")
    
    def _print_summary(self):
        """Print summary statistics"""
        print("\n=== Pipeline Summary ===")
        print(f"Total chunks processed: {self.stats['total_chunks']}")
        print(f"Relevant spans found: {self.stats['pre_filtered_spans']} "
              f"({100 * self.stats['pre_filtered_spans'] / max(1, self.stats['total_chunks']):.1f}%)")
        print(f"Spans with bottleneck matches: {self.stats['classified_spans']}")
        print(f"Final accepted evidence: {self.stats['accepted_evidence']}")
        print(f"Rejected after validation: {self.stats['rejected_evidence']}")
        
        # Efficiency metrics
        if self.stats['total_chunks'] > 0:
            reduction = 100 * (1 - self.stats['pre_filtered_spans'] / self.stats['total_chunks'])
            print(f"\nPre-filter reduction: {reduction:.1f}%")
        
        if self.stats['pre_filtered_spans'] > 0:
            precision = 100 * self.stats['accepted_evidence'] / self.stats['pre_filtered_spans']
            print(f"Final precision: {precision:.1f}%")
    
    def explain_evidence(self, evidence: FinalEvidence) -> str:
        """Get detailed explanation for a piece of evidence"""
        return self.arbitrator.explain_decision(evidence)