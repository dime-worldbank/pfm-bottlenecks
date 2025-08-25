"""
Database operations for PFM Bottleneck Analysis
Handles reading from and writing to Spark tables in Databricks
"""
import pandas as pd
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages database operations for the bottleneck analysis pipeline"""
    
    def __init__(self, spark, database_name: str = "prd_mega.sboost4"):
        """
        Initialize database manager
        
        Args:
            spark: Spark session
            database_name: Default database name for operations
        """
        self.spark = spark
        self.database_name = database_name
    
    def read_chunks(self, table_name: str = "per_pfr_chunks", 
                   node_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Read document chunks from Spark table
        
        Args:
            table_name: Name of the chunks table
            node_ids: Optional list of node IDs to filter
            
        Returns:
            DataFrame with chunks
        """
        query = f"SELECT * FROM {self.database_name}.{table_name}"
        df = self.spark.sql(query).toPandas()
        
        if node_ids:
            df = df[df.node_id.isin(node_ids)]
        
        return df
    
    def read_document_metadata(self, 
                              table_name: str = "per_pfr_document_data") -> pd.DataFrame:
        """
        Read document metadata from Spark table
        
        Args:
            table_name: Name of the metadata table
            
        Returns:
            DataFrame with document metadata
        """
        columns_to_keep = [
            'node_id',
            'cntry_name',
            'doc_date',
            'doc_name',
            'ent_topic_text',
            'ext_pdf_url',
            'ext_text_url'
        ]
        
        query = f"SELECT {', '.join(columns_to_keep)} FROM {self.database_name}.{table_name}"
        return self.spark.sql(query).toPandas()
    
    def read_extraction_results(self, bottleneck_id: str) -> pd.DataFrame:
        """
        Read extraction results for a specific bottleneck
        
        Args:
            bottleneck_id: ID of the bottleneck (e.g., "1_1")
            
        Returns:
            DataFrame with extraction results
        """
        table_name = f"extraction_bottleneck_{bottleneck_id.replace('.', '_')}"
        query = f"SELECT * FROM {self.database_name}.{table_name}"
        return self.spark.sql(query).toPandas()
    
    def read_validation_results(self, bottleneck_id: str) -> pd.DataFrame:
        """
        Read validation results for a specific bottleneck
        
        Args:
            bottleneck_id: ID of the bottleneck (e.g., "1_1")
            
        Returns:
            DataFrame with validation results
        """
        table_name = f"validation_bottleneck_{bottleneck_id.replace('.', '_')}"
        query = f"SELECT * FROM {self.database_name}.{table_name}"
        return self.spark.sql(query).toPandas()
    
    def write_extraction_results(self, df: pd.DataFrame, bottleneck_id: str):
        """
        Write extraction results to database
        
        Args:
            df: DataFrame with extraction results
            bottleneck_id: ID of the bottleneck
        """
        table_name = f"extraction_bottleneck_{bottleneck_id.replace('.', '_')}"
        self._write_to_table(df, table_name)
    
    def write_validation_results(self, df: pd.DataFrame, bottleneck_id: str):
        """
        Write validation results to database
        
        Args:
            df: DataFrame with validation results
            bottleneck_id: ID of the bottleneck
        """
        table_name = f"validation_bottleneck_{bottleneck_id.replace('.', '_')}"
        self._write_to_table(df, table_name)
    
    def write_final_results(self, df: pd.DataFrame, bottleneck_id: str):
        """
        Write final formatted results to database
        
        Args:
            df: DataFrame with final results
            bottleneck_id: ID of the bottleneck
        """
        table_name = f"final_bottleneck_{bottleneck_id.replace('.', '_')}"
        self._write_to_table(df, table_name)
    
    def _write_to_table(self, df: pd.DataFrame, table_name: str):
        """
        Write DataFrame to Spark table
        
        Args:
            df: DataFrame to write
            table_name: Name of the target table
        """
        # Ensure database exists
        self.spark.sql(f"""
            CREATE DATABASE IF NOT EXISTS {self.database_name.split('.')[0]}.{self.database_name.split('.')[1]}
        """)
        
        # Write to table
        sdf = self.spark.createDataFrame(df)
        sdf.write.mode("overwrite").option("mergeSchema", "true").saveAsTable(
            f"{self.database_name}.{table_name}"
        )
    
    def get_filtered_documents(self, countries: List[str], 
                              doc_types: List[str] = None) -> pd.DataFrame:
        """
        Get filtered documents based on criteria
        
        Args:
            countries: List of country names
            doc_types: Optional list of document types
            
        Returns:
            DataFrame with filtered documents
        """
        # Build country filter
        country_conditions = " OR ".join([f"cntry_name = '{c}'" for c in countries])
        
        # Build doc type filter if provided
        doc_type_condition = ""
        if doc_types:
            doc_type_conditions = " OR ".join([f"doc_type_name = '{dt}'" for dt in doc_types])
            doc_type_condition = f" AND ({doc_type_conditions})"
        
        query = f"""
        SELECT *
        FROM prd_corpdata.dm_reference_gold.v_dim_imagebank_document
        WHERE ({country_conditions})
        {doc_type_condition}
        AND lang_name = 'English'
        AND disclsr_stat_name = 'Disclosed'
        ORDER BY doc_date DESC
        """
        
        return self.spark.sql(query).toPandas()