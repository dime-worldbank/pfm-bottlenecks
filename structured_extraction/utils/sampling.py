"""
Sampling utilities for managing review workload
"""
import pandas as pd
from typing import Optional
import numpy as np


class SamplingStrategy:
    """Strategies for sampling evidence for expert review"""
    
    @staticmethod
    def sample_for_review(df: pd.DataFrame, max_samples: int = 100,
                         strategy: str = "stratified", 
                         confidence_column: str = None) -> pd.DataFrame:
        """
        Sample evidence for expert review
        
        Args:
            df: DataFrame with evidence to sample
            max_samples: Maximum number of samples to return
            strategy: Sampling strategy ('random', 'stratified', 'confidence')
            confidence_column: Column name for confidence-based sampling
            
        Returns:
            Sampled DataFrame
        """
        if len(df) <= max_samples:
            return df
        
        if strategy == "random":
            return df.sample(n=max_samples, random_state=42)
        
        elif strategy == "stratified":
            # Stratify by confidence level if available
            if confidence_column and confidence_column in df.columns:
                return SamplingStrategy._stratified_sample(
                    df, max_samples, confidence_column
                )
            else:
                # Fall back to random if no confidence column
                return df.sample(n=max_samples, random_state=42)
        
        elif strategy == "confidence":
            # Prioritize borderline confidence cases
            if confidence_column and confidence_column in df.columns:
                return SamplingStrategy._confidence_based_sample(
                    df, max_samples, confidence_column
                )
            else:
                return df.sample(n=max_samples, random_state=42)
        
        else:
            raise ValueError(f"Unknown sampling strategy: {strategy}")
    
    @staticmethod
    def _stratified_sample(df: pd.DataFrame, max_samples: int, 
                          stratify_column: str) -> pd.DataFrame:
        """
        Perform stratified sampling
        
        Args:
            df: DataFrame to sample from
            max_samples: Maximum samples to return
            stratify_column: Column to stratify by
            
        Returns:
            Stratified sample
        """
        # Get unique values and their proportions
        value_counts = df[stratify_column].value_counts()
        proportions = value_counts / len(df)
        
        sampled_dfs = []
        for value, proportion in proportions.items():
            n_samples = int(np.ceil(proportion * max_samples))
            value_df = df[df[stratify_column] == value]
            
            if len(value_df) <= n_samples:
                sampled_dfs.append(value_df)
            else:
                sampled_dfs.append(value_df.sample(n=n_samples, random_state=42))
        
        result = pd.concat(sampled_dfs, ignore_index=True)
        
        # Trim to exact max_samples if we went over
        if len(result) > max_samples:
            result = result.sample(n=max_samples, random_state=42)
        
        return result
    
    @staticmethod
    def _confidence_based_sample(df: pd.DataFrame, max_samples: int,
                                confidence_column: str) -> pd.DataFrame:
        """
        Sample prioritizing borderline confidence cases
        
        Args:
            df: DataFrame to sample from
            max_samples: Maximum samples to return
            confidence_column: Column with confidence values
            
        Returns:
            Confidence-weighted sample
        """
        # Define weights - higher weight for borderline cases
        weights = df[confidence_column].map({
            "strong": 0.2,
            "borderline": 0.6,
            "weak": 0.2,
            "high": 0.2,
            "medium": 0.6,
            "low": 0.2
        }).fillna(0.33)  # Default weight if unknown value
        
        # Normalize weights
        weights = weights / weights.sum()
        
        # Sample with weights
        sampled_indices = np.random.choice(
            df.index, 
            size=min(max_samples, len(df)),
            replace=False,
            p=weights
        )
        
        return df.loc[sampled_indices]
    
    @staticmethod
    def combine_expert_samples(df_model: pd.DataFrame, 
                             df_expert: pd.DataFrame) -> pd.DataFrame:
        """
        Combine model results with expert-reviewed samples
        
        Args:
            df_model: Full model results
            df_expert: Expert-reviewed subset
            
        Returns:
            Combined DataFrame with review status
        """
        # Mark expert-reviewed samples
        merge_keys = ["node_id", "chunk_id"]
        
        # Add review flag to model results
        df_model["was_reviewed"] = False
        
        # Update with expert reviews
        for _, row in df_expert.iterrows():
            mask = (
                (df_model["node_id"] == row["node_id"]) & 
                (df_model["chunk_id"] == row["chunk_id"])
            )
            df_model.loc[mask, "was_reviewed"] = True
            df_model.loc[mask, "Review_status"] = row.get("Review_status", "")
            df_model.loc[mask, "Reason"] = row.get("Reason", "")
        
        return df_model