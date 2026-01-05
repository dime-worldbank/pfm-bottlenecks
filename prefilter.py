"""
Pre-Filter using dense embeddings only.
"""

import numpy as np
import pandas as pd
from typing import List
from sentence_transformers import SentenceTransformer
from pyspark.sql import SparkSession
from consts import LOCAL_EMBEDDINGS_MODEL
from bottleneck_definitions import BOTTLENECK_DATA


def _l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if x.ndim == 1:
        x = x[None, :]
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(norms, eps)


class PreFilter:
    def __init__(
        self,
        embedding_model: str = LOCAL_EMBEDDINGS_MODEL,
        embedding_threshold: float = 0.55,
        encode_batch_size: int = 100,
        show_progress: bool = True,
        dtype=np.float32,
    ):
        self.embedding_threshold = float(embedding_threshold)
        self.encode_batch_size = encode_batch_size
        self.show_progress = show_progress
        self.dtype = dtype
        self.encoder = SentenceTransformer(embedding_model)

        self._create_reference_embeddings()

    def _create_reference_embeddings(self):
        reference_texts: List[str] = []

        for challenge in BOTTLENECK_DATA["challenges"].values():
            for bottleneck in challenge["bottlenecks"]:
                text = f"{bottleneck['name']}. {bottleneck['description']}"
                reference_texts.append(text)

        if not reference_texts:
            self.reference_embeddings = np.empty((0, 0), dtype=self.dtype)
            return

        ref_emb = self.encoder.encode(
            reference_texts,
            batch_size=self.encode_batch_size,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        ).astype(self.dtype, copy=False)

        ref_emb = _l2_normalize(ref_emb).astype(self.dtype, copy=False)
        self.reference_embeddings = np.ascontiguousarray(ref_emb)

    def filter_batch(self, chunk_texts: List[str]) -> List[bool]:
        if not chunk_texts:
            return []

        if self.reference_embeddings.size == 0:
            return [False for _ in chunk_texts]

        text_embs = self.encoder.encode(
            chunk_texts,
            batch_size=self.encode_batch_size,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        ).astype(self.dtype, copy=False)
        text_embs = _l2_normalize(text_embs).astype(self.dtype, copy=False)
        text_embs = np.ascontiguousarray(text_embs)

        sim_matrix = text_embs @ self.reference_embeddings.T
        max_sims = sim_matrix.max(axis=1)

        return [bool(sim >= self.embedding_threshold) for sim in max_sims]

    def max_similarity_batch(self, chunk_texts: List[str]) -> List[float]:
        if not chunk_texts:
            return []

        if self.reference_embeddings.size == 0:
            return [0.0 for _ in chunk_texts]

        text_embs = self.encoder.encode(
            chunk_texts,
            batch_size=self.encode_batch_size,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        ).astype(self.dtype, copy=False)
        text_embs = _l2_normalize(text_embs).astype(self.dtype, copy=False)
        text_embs = np.ascontiguousarray(text_embs)

        sim_matrix = text_embs @ self.reference_embeddings.T
        max_sims = sim_matrix.max(axis=1)

        return [float(sim) for sim in max_sims]


def run_prefilter(spark: SparkSession, schema: str, source_table: str, results_table: str, threshold: float = 0.55):
    """Run prefilter on new chunks and save results to Databricks table."""

    source_df = spark.table(f"{schema}.{source_table}").select("node_id", "chunk_id").toPandas()
    source_pairs = set(zip(source_df['node_id'], source_df['chunk_id']))

    try:
        processed_df = spark.table(f"{schema}.{results_table}").select("node_id", "chunk_id").toPandas()
        processed_pairs = set(zip(processed_df['node_id'], processed_df['chunk_id']))
    except Exception:
        processed_pairs = set()

    new_pairs = source_pairs - processed_pairs
    print(f"Source: {len(source_pairs)} | Processed: {len(processed_pairs)} | New: {len(new_pairs)}")

    if new_pairs:
        new_pairs_df = pd.DataFrame(list(new_pairs), columns=['node_id', 'chunk_id'])
        spark_new_pairs = spark.createDataFrame(new_pairs_df)

        new_chunks_df = spark.table(f"{schema}.{source_table}").join(
            spark_new_pairs, on=['node_id', 'chunk_id'], how='inner'
        ).toPandas()

        prefilter = PreFilter(embedding_threshold=threshold, show_progress=True)
        print(f"Loaded {len(new_chunks_df)} chunks, {len(prefilter.reference_embeddings)} reference embeddings")

        filter_results = prefilter.filter_batch(new_chunks_df['text'].tolist())
        new_chunks_df['prefilter_passed'] = filter_results

        passed = sum(filter_results)
        print(f"Results: {passed}/{len(filter_results)} passed ({100*passed/len(filter_results):.1f}%)")

        results_df = new_chunks_df[['node_id', 'chunk_id', 'prefilter_passed']]
        spark_df = spark.createDataFrame(results_df)

        mode = "append" if processed_pairs else "overwrite"
        spark_df.write.mode(mode).saveAsTable(f"{schema}.{results_table}")
        print(f"Saved to {schema}.{results_table}")
    else:
        print("No new chunks to process")

    total_df = spark.table(f"{schema}.{results_table}").toPandas()
    total_passed = total_df['prefilter_passed'].sum()
    total_count = len(total_df)
    print(f"Total: {total_count} | Passed: {total_passed} ({100*total_passed/total_count:.1f}%)")
