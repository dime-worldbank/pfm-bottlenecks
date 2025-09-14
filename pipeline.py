"""
PFM Bottleneck Analysis Pipeline - Complete Implementation
Stages:
1. Prefilter (0 LLM calls) - Embedding-based filtering
2. Multi-Challenge Classification (1 LLM call) - Identify relevant challenges
3. Evidence Extraction (N LLM calls) - Extract evidence for each bottleneck
4. Agentic Validation (3 LLM calls per evidence) - Validate with advocate/skeptic/judge
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Import all stage components
from bottleneck_definitions import load_bottlenecks
from prefilter import PreFilter
from challenge_classification import ChallengeClassifier
from evidence_extraction import EvidenceExtractor
from agents.advocate import AdvocateAgent
from agents.skeptic import SkepticAgent
from agents.judge import JudgeAgent
from agents.models import EvidenceInput


class StageStatus(str, Enum):
    """Pipeline stage status tracking."""
    STARTED = "started"
    PREFILTER_FAILED = "prefilter_failed"
    PREFILTER_PASSED = "prefilter_passed"
    CLASSIFICATION_FAILED = "classification_failed"
    CLASSIFICATION_PASSED = "classification_passed"
    EXTRACTION_FAILED = "extraction_failed"
    EXTRACTION_PASSED = "extraction_passed"
    VALIDATION_FAILED = "validation_failed"
    VALIDATION_PASSED = "validation_passed"
    COMPLETED = "completed"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    # Stage toggles
    use_prefilter: bool = True
    use_classification: bool = True
    use_extraction: bool = True
    use_validation: bool = True
    
    # Model configuration
    classification_model: str = "openai/gpt-4o-mini"
    extraction_model: str = "openai/gpt-4o-mini"
    validation_model: str = "openai/gpt-4o-mini"
    
    # Thresholds
    classification_threshold: float = 0.60
    extraction_min_confidence: str = "moderate"  # weak, moderate, strong
    validation_acceptance_threshold: float = 0.5
    
    # Processing
    batch_size: int = 100
    max_bottlenecks_per_chunk: int = 10  # Limit extraction calls
    
    # Logging
    log_file: str = "pipeline.log"
    save_intermediate: bool = True
    output_dir: str = "pipeline_output"


@dataclass
class ChunkResult:
    """Results for a single chunk through the pipeline."""
    # Identifiers
    chunk_id: str
    node_id: Optional[str] = None
    chunk_text: str = ""
    
    # Stage status
    stage_reached: StageStatus = StageStatus.STARTED
    
    # Stage 1: Prefilter
    prefilter_passed: bool = False
    prefilter_hints: List[str] = field(default_factory=list)
    
    # Stage 2: Classification
    challenges_identified: List[Dict] = field(default_factory=list)
    
    # Stage 3: Extraction
    evidence_extracted: List[Dict] = field(default_factory=list)
    
    # Stage 4: Validation
    evidence_validated: List[Dict] = field(default_factory=list)
    
    # Metadata
    processing_time: float = 0.0
    llm_calls: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'chunk_id': self.chunk_id,
            'node_id': self.node_id,
            'stage_reached': self.stage_reached,
            'prefilter_passed': self.prefilter_passed,
            'prefilter_hints': self.prefilter_hints,
            'challenges_identified': self.challenges_identified,
            'evidence_extracted': self.evidence_extracted,
            'evidence_validated': self.evidence_validated,
            'processing_time': self.processing_time,
            'llm_calls': self.llm_calls,
            'errors': self.errors
        }


class PFMPipeline:
    """
    Complete PFM Bottleneck Analysis Pipeline.
    Processes chunks through 4 stages to identify and validate bottleneck evidence.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None, service=None):
        """
        Initialize the pipeline with configuration.
        
        Args:
            config: Pipeline configuration
            service: Optional shared Service instance for LLM calls
        """
        self.config = config or PipelineConfig()
        self.bottleneck_data = load_bottlenecks()
        self.logger = self._setup_logging()
        
        # Initialize service (shared across all components)
        if service:
            self.service = service
        else:
            from service import Service
            self.service = Service()
        
        # Initialize stage components
        if self.config.use_prefilter:
            self.prefilter = PreFilter()
        else:
            self.prefilter = None
            
        if self.config.use_classification:
            self.classifier = ChallengeClassifier(
                model=self.config.classification_model,
                confidence_threshold=self.config.classification_threshold,
                service=self.service
            )
        else:
            self.classifier = None
            
        if self.config.use_extraction:
            self.extractor = EvidenceExtractor(
                service=self.service,
                model=self.config.extraction_model
            )
        else:
            self.extractor = None
            
        if self.config.use_validation:
            self.advocate = AdvocateAgent(service=self.service, model=self.config.validation_model)
            self.skeptic = SkepticAgent(service=self.service, model=self.config.validation_model)
            self.judge = JudgeAgent(service=self.service, model=self.config.validation_model)
        else:
            self.advocate = self.skeptic = self.judge = None
        
        # Create output directory
        Path(self.config.output_dir).mkdir(exist_ok=True)
        
        self.logger.info(
            f"Pipeline initialized - Stages enabled: "
            f"prefilter={self.config.use_prefilter}, "
            f"classification={self.config.use_classification}, "
            f"extraction={self.config.use_extraction}, "
            f"validation={self.config.use_validation}"
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_bottlenecks_for_challenge(self, challenge_id: str) -> List[str]:
        """Get all bottleneck IDs for a given challenge."""
        challenge_num = int(challenge_id)
        challenge = self.bottleneck_data['challenges'].get(challenge_num)
        if not challenge:
            return []
        return [b['id'] for b in challenge.get('bottlenecks', [])]
    
    def process_chunk(self, 
                     chunk_text: str, 
                     chunk_id: Optional[str] = None,
                     node_id: Optional[str] = None) -> ChunkResult:
        """
        Process a single chunk through all pipeline stages.
        
        Args:
            chunk_text: The text to analyze
            chunk_id: Chunk identifier
            node_id: Node identifier
            
        Returns:
            ChunkResult with all processing information
        """
        import time
        start_time = time.time()
        
        # Initialize result
        if not chunk_id:
            chunk_id = f"chunk_{datetime.now().timestamp()}"
        
        result = ChunkResult(
            chunk_id=chunk_id,
            node_id=node_id,
            chunk_text=chunk_text
        )
        
        try:
            # Stage 1: Prefilter
            if self.config.use_prefilter:
                result = self._stage1_prefilter(chunk_text, result)
                if not result.prefilter_passed:
                    result.stage_reached = StageStatus.PREFILTER_FAILED
                    result.processing_time = time.time() - start_time
                    return result
            else:
                result.prefilter_passed = True
            
            # Stage 2: Multi-Challenge Classification
            if self.config.use_classification:
                result = self._stage2_classification(chunk_text, result)
                if not result.challenges_identified:
                    result.stage_reached = StageStatus.CLASSIFICATION_FAILED
                    result.processing_time = time.time() - start_time
                    return result
            
            # Stage 3: Evidence Extraction
            if self.config.use_extraction and result.challenges_identified:
                result = self._stage3_extraction(chunk_text, result)
                if not result.evidence_extracted:
                    result.stage_reached = StageStatus.EXTRACTION_FAILED
                    result.processing_time = time.time() - start_time
                    return result
            
            # Stage 4: Agentic Validation
            if self.config.use_validation and result.evidence_extracted:
                result = self._stage4_validation(chunk_text, result)
            
            result.stage_reached = StageStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Error processing chunk {chunk_id}: {str(e)}")
            result.errors.append(str(e))
        
        result.processing_time = time.time() - start_time
        return result
    
    def _stage1_prefilter(self, text: str, result: ChunkResult) -> ChunkResult:
        """Stage 1: Prefilter using embeddings."""
        try:
            is_relevant, hints = self.prefilter.filter(text)
            result.prefilter_passed = is_relevant
            result.prefilter_hints = hints if hints else []
            
            if is_relevant:
                result.stage_reached = StageStatus.PREFILTER_PASSED
                self.logger.debug(f"Chunk {result.chunk_id} passed prefilter")
            else:
                self.logger.debug(f"Chunk {result.chunk_id} filtered out")
                
        except Exception as e:
            self.logger.error(f"Prefilter error for {result.chunk_id}: {str(e)}")
            result.errors.append(f"Prefilter: {str(e)}")
            result.prefilter_passed = True  # Continue on error
            
        return result
    
    def _stage2_classification(self, text: str, result: ChunkResult) -> ChunkResult:
        """Stage 2: Multi-challenge classification."""
        try:
            decision = self.classifier.classify(text)
            result.llm_calls += 1
            
            if decision.accepted and decision.accepted_labels:
                result.challenges_identified = [
                    {
                        'challenge_id': label.challenge_id.value,
                        'score': float(label.score),
                        'evidence_span': label.evidence_span,
                        'rationale': label.rationale
                    }
                    for label in decision.accepted_labels
                ]
                result.stage_reached = StageStatus.CLASSIFICATION_PASSED
                self.logger.debug(
                    f"Chunk {result.chunk_id} classified: "
                    f"{len(result.challenges_identified)} challenges"
                )
            else:
                self.logger.debug(f"Chunk {result.chunk_id}: No challenges identified")
                
        except Exception as e:
            self.logger.error(f"Classification error for {result.chunk_id}: {str(e)}")
            result.errors.append(f"Classification: {str(e)}")
            
        return result
    
    def _stage3_extraction(self, text: str, result: ChunkResult) -> ChunkResult:
        """Stage 3: Evidence extraction for identified challenges."""
        try:
            all_extractions = []
            
            # For each identified challenge, extract evidence for its bottlenecks
            for challenge in result.challenges_identified[:self.config.max_bottlenecks_per_chunk]:
                challenge_id = challenge['challenge_id']
                bottleneck_ids = self.get_bottlenecks_for_challenge(challenge_id)
                
                for bottleneck_id in bottleneck_ids:
                    evidence = self.extractor.extract_evidence(text, bottleneck_id)
                    result.llm_calls += 1
                    
                    if evidence and evidence.evidence_span:
                        # Check confidence threshold
                        if (self.config.extraction_min_confidence == "weak" or
                            (self.config.extraction_min_confidence == "moderate" and 
                             evidence.confidence.value in ["moderate", "strong"]) or
                            (self.config.extraction_min_confidence == "strong" and 
                             evidence.confidence.value == "strong")):
                            
                            all_extractions.append({
                                'bottleneck_id': bottleneck_id,
                                'challenge_id': challenge_id,
                                'evidence_span': evidence.evidence_span,
                                'confidence': evidence.confidence.value,
                                'reasoning': evidence.reasoning,
                                'span_start': evidence.span_start,
                                'span_end': evidence.span_end
                            })
            
            result.evidence_extracted = all_extractions
            if all_extractions:
                result.stage_reached = StageStatus.EXTRACTION_PASSED
                self.logger.debug(
                    f"Chunk {result.chunk_id}: "
                    f"{len(all_extractions)} evidence spans extracted"
                )
            else:
                self.logger.debug(f"Chunk {result.chunk_id}: No evidence extracted")
                
        except Exception as e:
            self.logger.error(f"Extraction error for {result.chunk_id}: {str(e)}")
            result.errors.append(f"Extraction: {str(e)}")
            
        return result
    
    def _stage4_validation(self, text: str, result: ChunkResult) -> ChunkResult:
        """Stage 4: Agentic validation of extracted evidence."""
        try:
            validated = []
            
            for evidence in result.evidence_extracted:
                # Prepare evidence input
                evidence_input = EvidenceInput(
                    chunk_id=result.chunk_id,
                    chunk_text=text,
                    bottleneck_id=evidence['bottleneck_id'],
                    evidence_span=evidence['evidence_span'],
                    span_start=evidence.get('span_start'),
                    span_end=evidence.get('span_end')
                )
                
                # Run three-agent validation
                advocate_arg = self.advocate.analyze(evidence_input)
                result.llm_calls += 1
                
                skeptic_arg = self.skeptic.analyze(evidence_input)
                result.llm_calls += 1
                
                judge_decision = self.judge.judge(evidence_input, advocate_arg, skeptic_arg)
                result.llm_calls += 1
                
                # Store validation results
                validation_result = {
                    'bottleneck_id': evidence['bottleneck_id'],
                    'challenge_id': evidence['challenge_id'],
                    'evidence_span': evidence['evidence_span'],
                    'extraction_confidence': evidence['confidence'],
                    'advocate_confidence': advocate_arg.overall_confidence,
                    'skeptic_weakness': skeptic_arg.weakness_score,
                    'judge_decision': judge_decision.decision,
                    'judge_confidence': judge_decision.confidence,
                    'judge_reasoning': judge_decision.reasoning,
                    'accepted': judge_decision.decision == 'accept'
                }
                
                validated.append(validation_result)
                
                self.logger.debug(
                    f"Validation for {evidence['bottleneck_id']}: "
                    f"{judge_decision.decision} (conf: {judge_decision.confidence:.2f})"
                )
            
            result.evidence_validated = validated
            
            # Check if any evidence was accepted
            if any(v['accepted'] for v in validated):
                result.stage_reached = StageStatus.VALIDATION_PASSED
            else:
                result.stage_reached = StageStatus.VALIDATION_FAILED
                
        except Exception as e:
            self.logger.error(f"Validation error for {result.chunk_id}: {str(e)}")
            result.errors.append(f"Validation: {str(e)}")
            
        return result
    
    def process_batch(self, chunks: List[Dict]) -> List[ChunkResult]:
        """
        Process multiple chunks efficiently.
        
        Args:
            chunks: List of dictionaries with 'text', 'chunk_id', 'node_id'
            
        Returns:
            List of ChunkResult objects
        """
        if not chunks:
            return []
        
        results = []
        total = len(chunks)
        
        # Stage 1: Batch prefilter (if available)
        if self.config.use_prefilter and hasattr(self.prefilter, 'filter_batch'):
            self.logger.info(f"Batch prefiltering {total} chunks...")
            
            texts = [c.get('text', c.get('chunk_text', '')) for c in chunks]
            filter_results = self.prefilter.filter_batch(texts)
            
            # Create initial results with prefilter info
            for i, (chunk, (is_relevant, hints)) in enumerate(zip(chunks, filter_results)):
                result = ChunkResult(
                    chunk_id=chunk.get('chunk_id', chunk.get('id', f'chunk_{i}')),
                    node_id=chunk.get('node_id'),
                    chunk_text=chunk.get('text', chunk.get('chunk_text', '')),
                    prefilter_passed=bool(is_relevant),
                    prefilter_hints=hints if hints else []
                )
                
                if is_relevant:
                    result.stage_reached = StageStatus.PREFILTER_PASSED
                else:
                    result.stage_reached = StageStatus.PREFILTER_FAILED
                    
                results.append(result)
                
            # Filter to only relevant chunks for further processing
            relevant_results = [r for r in results if r.prefilter_passed]
            self.logger.info(
                f"Prefilter complete: {len(relevant_results)}/{total} chunks passed"
            )
        else:
            # No batch prefilter, create initial results
            for i, chunk in enumerate(chunks):
                result = ChunkResult(
                    chunk_id=chunk.get('chunk_id', chunk.get('id', f'chunk_{i}')),
                    node_id=chunk.get('node_id'),
                    chunk_text=chunk.get('text', chunk.get('chunk_text', '')),
                    prefilter_passed=True
                )
                results.append(result)
            relevant_results = results
        
        # Process remaining stages individually
        for i, result in enumerate(relevant_results):
            if not result.prefilter_passed:
                continue
                
            self.logger.info(
                f"Processing chunk {i+1}/{len(relevant_results)}: {result.chunk_id}"
            )
            
            # Continue from Stage 2
            if self.config.use_classification:
                result = self._stage2_classification(result.chunk_text, result)
                
            if self.config.use_extraction and result.challenges_identified:
                result = self._stage3_extraction(result.chunk_text, result)
                
            if self.config.use_validation and result.evidence_extracted:
                result = self._stage4_validation(result.chunk_text, result)
        
        # Log summary statistics
        self._log_batch_summary(results)
        
        return results
    
    def _log_batch_summary(self, results: List[ChunkResult]):
        """Log summary statistics for batch processing."""
        total = len(results)
        stages = {
            'prefilter_passed': sum(1 for r in results if r.prefilter_passed),
            'classification_passed': sum(1 for r in results if r.challenges_identified),
            'extraction_passed': sum(1 for r in results if r.evidence_extracted),
            'validation_passed': sum(1 for r in results if any(
                v.get('accepted', False) for v in r.evidence_validated
            ))
        }
        
        total_llm_calls = sum(r.llm_calls for r in results)
        total_time = sum(r.processing_time for r in results)
        
        self.logger.info(
            f"\nBatch Summary ({total} chunks):\n"
            f"  Prefilter passed: {stages['prefilter_passed']}\n"
            f"  Classification passed: {stages['classification_passed']}\n"
            f"  Extraction passed: {stages['extraction_passed']}\n"
            f"  Validation passed: {stages['validation_passed']}\n"
            f"  Total LLM calls: {total_llm_calls}\n"
            f"  Total processing time: {total_time:.2f}s"
        )
    
    def save_results(self, results: List[ChunkResult], filename: Optional[str] = None):
        """Save pipeline results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_results_{timestamp}.json"
        
        output_path = Path(self.config.output_dir) / filename
        
        # Convert results to dictionaries
        results_dict = [r.to_dict() for r in results]
        
        # Add metadata
        output = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_chunks': len(results),
                'config': {
                    'use_prefilter': self.config.use_prefilter,
                    'use_classification': self.config.use_classification,
                    'use_extraction': self.config.use_extraction,
                    'use_validation': self.config.use_validation,
                    'classification_threshold': self.config.classification_threshold,
                    'extraction_min_confidence': self.config.extraction_min_confidence
                }
            },
            'results': results_dict
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        self.logger.info(f"Results saved to {output_path}")
        return str(output_path)
    
    def get_accepted_evidence(self, results: List[ChunkResult]) -> List[Dict]:
        """Extract all accepted evidence from results."""
        accepted = []
        
        for result in results:
            for evidence in result.evidence_validated:
                if evidence.get('accepted'):
                    accepted.append({
                        'chunk_id': result.chunk_id,
                        'node_id': result.node_id,
                        'bottleneck_id': evidence['bottleneck_id'],
                        'challenge_id': evidence['challenge_id'],
                        'evidence_span': evidence['evidence_span'],
                        'judge_confidence': evidence['judge_confidence'],
                        'judge_reasoning': evidence['judge_reasoning']
                    })
        
        return accepted