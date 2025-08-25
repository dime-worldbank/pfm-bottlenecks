"""
Excel export utilities for PFM Bottleneck Analysis
"""
import pandas as pd
import tempfile
import shutil
from typing import Dict, List, Optional
import os


class ExcelExporter:
    """Handles Excel file generation for review and reporting"""
    
    def __init__(self, output_path: str = None):
        """
        Initialize Excel exporter
        
        Args:
            output_path: Base path for Excel outputs
        """
        self.output_path = output_path or "/Volumes/prd_mega/sboost4/vboost4/Documents/input/Bottleneck"
    
    def export_for_review(self, df: pd.DataFrame, bottleneck_id: str, 
                         filename: str = None) -> str:
        """
        Export DataFrame to Excel for expert review
        
        Args:
            df: DataFrame to export
            bottleneck_id: ID of the bottleneck
            filename: Optional custom filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"bottleneck_{bottleneck_id.replace('.', '_')}_for_review.xlsx"
        
        filepath = os.path.join(self.output_path, filename)
        
        # Prepare columns for review
        review_columns = self._prepare_review_columns(df, bottleneck_id)
        
        # Export to Excel
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
            temp_path = tmp.name
            
            with pd.ExcelWriter(temp_path, engine="xlsxwriter") as writer:
                sheet_name = str(bottleneck_id)[:31]  # Excel sheet name limit
                review_columns.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(review_columns.columns):
                    column_width = max(review_columns[col].astype(str).str.len().max(), len(col))
                    column_width = min(column_width, 50)  # Cap at 50 characters
                    worksheet.set_column(i, i, column_width)
            
            shutil.copy(temp_path, filepath)
        
        print(f"Exported to: {filepath}")
        return filepath
    
    def export_multi_bottleneck(self, results_dict: Dict[str, pd.DataFrame], 
                               filename: str = "all_bottlenecks_review.xlsx") -> str:
        """
        Export multiple bottleneck results to a single Excel file
        
        Args:
            results_dict: Dictionary mapping bottleneck_id to DataFrame
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        filepath = os.path.join(self.output_path, filename)
        
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
            temp_path = tmp.name
            
            with pd.ExcelWriter(temp_path, engine="xlsxwriter") as writer:
                for bottleneck_id, df in results_dict.items():
                    sheet_name = str(bottleneck_id)[:31]
                    review_df = self._prepare_review_columns(df, bottleneck_id)
                    review_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            shutil.copy(temp_path, filepath)
        
        print(f"Exported multi-bottleneck file to: {filepath}")
        return filepath
    
    def merge_with_expert_review(self, model_results: pd.DataFrame, 
                                expert_review: pd.DataFrame) -> pd.DataFrame:
        """
        Merge model results with expert review feedback
        
        Args:
            model_results: DataFrame with model outputs
            expert_review: DataFrame with expert review columns
            
        Returns:
            Merged DataFrame
        """
        # Ensure we have the key columns
        merge_keys = ["node_id", "chunk_id"]
        
        # Merge on key columns
        merged = model_results.merge(
            expert_review[merge_keys + ["Review_status", "Reason"]], 
            on=merge_keys,
            how="left"
        )
        
        return merged
    
    def _prepare_review_columns(self, df: pd.DataFrame, bottleneck_id: str) -> pd.DataFrame:
        """
        Prepare DataFrame columns for review format
        
        Args:
            df: Original DataFrame
            bottleneck_id: ID of the bottleneck
            
        Returns:
            DataFrame with review columns
        """
        # Select and order columns for review
        review_columns = []
        
        # Core identification columns
        if "bottleneck_id" not in df.columns:
            df["bottleneck_id"] = bottleneck_id
        review_columns.extend(["bottleneck_id", "node_id", "chunk_id"])
        
        # Evidence columns
        if "extracted_evidence" in df.columns:
            review_columns.append("extracted_evidence")
        if "final_summary" in df.columns:
            review_columns.append("final_summary")
        
        # Validation columns
        if "is_valid" in df.columns:
            review_columns.append("is_valid")
        if "should_admit" in df.columns:
            review_columns.append("should_admit")
        if "validation_reasoning" in df.columns:
            review_columns.append("validation_reasoning")
        
        # Review columns (to be filled by experts)
        df["Review_status"] = ""
        df["Reason"] = ""
        review_columns.extend(["Review_status", "Reason"])
        
        # Document metadata
        metadata_cols = ["cntry_name", "doc_date", "doc_name", "ext_pdf_url"]
        for col in metadata_cols:
            if col in df.columns:
                review_columns.append(col)
        
        # Original chunk text
        if "chunk" in df.columns:
            review_columns.append("chunk")
        
        # Select only available columns
        available_columns = [col for col in review_columns if col in df.columns]
        
        return df[available_columns]