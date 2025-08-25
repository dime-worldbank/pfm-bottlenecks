"""
Main pipeline orchestration for PFM Bottleneck Analysis
"""
import pandas as pd
from typing import List, Dict, Optional, Any
from time import sleep
from tqdm import tqdm

from ..bottlenecks import load_bottleneck
from ..formatting.prompts import make_bottleneck_prompt, make_validation_prompt
from ..formatting.summarization import SummarizationService
import config


class BottleneckPipeline:
    """Main pipeline for bottleneck extraction, validation, and formatting"""
    
    def __init__(self, llm_service, db_manager, model: str = None):
        """
        Initialize the pipeline
        
        Args:
            llm_service: Azure OpenAI service instance
            db_manager: Database manager instance
            model: LLM model to use (defaults to config.LLM_MODEL)
        """
        self.llm_service = llm_service
        self.db_manager = db_manager
        self.model = model or config.LLM_MODEL
        self.summarization_service = SummarizationService(llm_service, self.model)
    
    def run_extraction(self, bottleneck_id: str, chunks: List[Dict], 
                      save_to_db: bool = True) -> pd.DataFrame:
        """
        Run extraction stage for a specific bottleneck
        
        Args:
            bottleneck_id: ID of the bottleneck to process
            chunks: List of chunk dictionaries with 'node_id', 'chunk_id', 'text'
            save_to_db: Whether to save results to database
            
        Returns:
            DataFrame with extraction results
        """
        print(f"Running extraction for bottleneck {bottleneck_id}...")
        
        # Load bottleneck configuration
        bottleneck = load_bottleneck(bottleneck_id)
        
        results = []
        for i, chunk in enumerate(tqdm(chunks, desc="Extracting evidence")):
            if i > 0 and i % config.BATCH_SIZE == 0:
                sleep(config.RATE_LIMIT_DELAY)
            
            try:
                prompt = make_bottleneck_prompt(
                    text=chunk["text"],
                    role_of_public_finance=bottleneck["role_of_public_finance"],
                    role_description=bottleneck["role_description"],
                    challenge_name=bottleneck["challenge_name"],
                    challenge_description=bottleneck["challenge_description"],
                    bottleneck_name=bottleneck["name"],
                    bottleneck_description=bottleneck["description"],
                    bottleneck_examples=bottleneck.get("examples")
                )
                
                result = self.llm_service.execute(
                    prompt=prompt,
                    model=self.model,
                    response_model=bottleneck["extraction_model"]
                )
                
                if result.extracted_evidence:
                    results.append({
                        "node_id": chunk["node_id"],
                        "chunk_id": chunk["chunk_id"],
                        "chunk": chunk["text"],
                        "bottleneck_id": bottleneck_id,
                        "extracted_evidence": result.extracted_evidence,
                        "reasoning": result.reasoning,
                        "extraction_confidence": result.confidence
                    })
            
            except Exception as e:
                print(f"Error processing chunk {chunk['chunk_id']}: {e}")
        
        df_results = pd.DataFrame(results)
        
        if save_to_db and not df_results.empty:
            self.db_manager.write_extraction_results(df_results, bottleneck_id)
            print(f"Saved {len(df_results)} extraction results to database")
        
        return df_results
    
    def run_validation(self, bottleneck_id: str, df_extracted: pd.DataFrame = None,
                      save_to_db: bool = True) -> pd.DataFrame:
        """
        Run validation stage for a specific bottleneck
        
        Args:
            bottleneck_id: ID of the bottleneck to process
            df_extracted: DataFrame with extraction results (if None, reads from DB)
            save_to_db: Whether to save results to database
            
        Returns:
            DataFrame with validation results
        """
        print(f"Running validation for bottleneck {bottleneck_id}...")
        
        # Load extraction results if not provided
        if df_extracted is None:
            df_extracted = self.db_manager.read_extraction_results(bottleneck_id)
        
        # Load bottleneck configuration
        bottleneck = load_bottleneck(bottleneck_id)
        
        validated_results = []
        for _, row in tqdm(df_extracted.iterrows(), total=len(df_extracted), 
                          desc="Validating evidence"):
            try:
                validation_prompt = make_validation_prompt(
                    extracted_evidence=row["extracted_evidence"],
                    reasoning=row["reasoning"],
                    role_of_public_finance=bottleneck["role_of_public_finance"],
                    role_description=bottleneck["role_description"],
                    challenge_name=bottleneck["challenge_name"],
                    challenge_description=bottleneck["challenge_description"],
                    bottleneck_name=bottleneck["name"],
                    bottleneck_description=bottleneck["description"],
                    validation_model_cls=bottleneck["validation_model"],
                    bottleneck_examples=bottleneck.get("examples")
                )
                
                validation = self.llm_service.execute(
                    prompt=validation_prompt,
                    model=self.model,
                    response_model=bottleneck["validation_model"]
                )
                
                # Combine extraction and validation results
                result = row.to_dict()
                result.update(validation.model_dump(exclude_unset=True))
                
                # Apply post-validation override if available
                if "post_validation_override" in bottleneck:
                    override_result = bottleneck["post_validation_override"](result)
                    result["matched_groups"] = override_result["matched_groups"]
                    result["should_admit"] = override_result["should_admit"]
                
                validated_results.append(result)
            
            except Exception as e:
                print(f"Error validating chunk {row['chunk_id']}: {e}")
        
        df_results = pd.DataFrame(validated_results)
        
        if save_to_db and not df_results.empty:
            self.db_manager.write_validation_results(df_results, bottleneck_id)
            print(f"Saved {len(df_results)} validation results to database")
        
        return df_results
    
    def run_formatting(self, bottleneck_id: str, df_validated: pd.DataFrame = None,
                      save_to_db: bool = True) -> pd.DataFrame:
        """
        Run formatting/summarization stage for a specific bottleneck
        
        Args:
            bottleneck_id: ID of the bottleneck to process
            df_validated: DataFrame with validation results (if None, reads from DB)
            save_to_db: Whether to save results to database
            
        Returns:
            DataFrame with formatted results
        """
        print(f"Running formatting for bottleneck {bottleneck_id}...")
        
        # Load validation results if not provided
        if df_validated is None:
            df_validated = self.db_manager.read_validation_results(bottleneck_id)
        
        # Filter to only valid results
        if "should_admit" in df_validated.columns:
            df_to_format = df_validated[df_validated["should_admit"] == True]
        else:
            df_to_format = df_validated[df_validated["is_valid"] == True]
        
        if df_to_format.empty:
            print("No valid evidence to format")
            return pd.DataFrame()
        
        # Load bottleneck configuration for examples
        bottleneck = load_bottleneck(bottleneck_id)
        
        # Get document metadata and chunks for context
        df_metadata = self.db_manager.read_document_metadata()
        df_chunks = self.db_manager.read_chunks()
        
        formatted_results = []
        for _, row in tqdm(df_to_format.iterrows(), total=len(df_to_format),
                          desc="Formatting evidence"):
            try:
                # Get context and metadata
                context_text = self.summarization_service.get_context(
                    df_chunks, row["node_id"], row["chunk_id"]
                )
                
                metadata_row = df_metadata[df_metadata.node_id == row["node_id"]].iloc[0]
                metadata_tuple = (
                    metadata_row["cntry_name"],
                    metadata_row["doc_name"],
                    metadata_row.get("admin_rgn_name", ""),
                    metadata_row.get("ent_topic_text", "")
                )
                
                # Extract structured fields
                structured = self.summarization_service.extract_structured_fields(
                    context_text=context_text,
                    extracted_evidence=row["extracted_evidence"],
                    bottleneck_name=bottleneck["name"],
                    bottleneck_description=bottleneck["description"],
                    metadata=metadata_tuple,
                    examples=bottleneck.get("examples", [])
                )
                
                # Create stylized summary
                summary = self.summarization_service.create_stylized_summary(
                    extracted_evidence=row["extracted_evidence"],
                    structured=structured,
                    bottleneck_name=bottleneck["name"],
                    examples=bottleneck.get("examples", [])
                )
                
                # Extract date range if relevant
                date_range = self.summarization_service.extract_date_range(
                    extended_context=context_text,
                    extracted_evidence=row["extracted_evidence"],
                    bottleneck_name=bottleneck["name"]
                )
                
                # Combine all results
                result = row.to_dict()
                result.update(structured.model_dump())
                result["final_summary"] = summary
                result["date_range"] = date_range
                result["extended_context"] = context_text
                
                formatted_results.append(result)
            
            except Exception as e:
                print(f"Error formatting chunk {row['chunk_id']}: {e}")
        
        df_results = pd.DataFrame(formatted_results)
        
        # Merge with metadata
        if not df_results.empty:
            df_results = df_results.merge(df_metadata, on="node_id", how="left")
            
            if save_to_db:
                self.db_manager.write_final_results(df_results, bottleneck_id)
                print(f"Saved {len(df_results)} formatted results to database")
        
        return df_results
    
    def run_full_pipeline(self, bottleneck_id: str, chunks: List[Dict]) -> Dict[str, pd.DataFrame]:
        """
        Run all three stages of the pipeline
        
        Args:
            bottleneck_id: ID of the bottleneck to process
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with DataFrames for each stage
        """
        # Stage 1: Extraction
        df_extracted = self.run_extraction(bottleneck_id, chunks)
        print(f"Extracted {len(df_extracted)} evidence chunks")
        
        # Stage 2: Validation
        df_validated = self.run_validation(bottleneck_id, df_extracted)
        valid_count = df_validated["should_admit"].sum() if "should_admit" in df_validated.columns else df_validated["is_valid"].sum()
        print(f"Validated {valid_count} chunks as true evidence")
        
        # Stage 3: Formatting
        df_formatted = self.run_formatting(bottleneck_id, df_validated)
        print(f"Formatted {len(df_formatted)} final summaries")
        
        return {
            "extraction": df_extracted,
            "validation": df_validated,
            "formatting": df_formatted
        }