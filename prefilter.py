"""
Pre-Filter using dense embeddings only.
NO LLM CALLS - uses local embeddings only.
Fast path: pre-normalize refs and texts → cosine = dot product.
"""

import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from bottleneck_definitions import load_bottlenecks


def _l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Row-wise L2 normalize (safe for zeros)."""
    if x.ndim == 1:
        x = x[None, :]
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(norms, eps)


class PreFilter:
    """
    Embedding-based filtering using semantic similarity.
    NO LLM calls - only local processing.
    """

    def __init__(
        self,
        embedding_model: str = "all-mpnet-base-v2",
        embedding_threshold: float = 0.55,
        encode_batch_size: int = 100,
        show_progress: bool = True,
        dtype=np.float32,
    ):
        """
        Args:
            embedding_model: Sentence transformer model name
            embedding_threshold: Min cosine similarity score
            encode_batch_size: Optional batch size override for encoding
            show_progress: Show ST encoding progress bars
            dtype: dtype for stored embeddings (default float32)
        """
        self.embedding_threshold = float(embedding_threshold)
        self.encode_batch_size = encode_batch_size
        self.show_progress = show_progress
        self.dtype = dtype

        # Load embedding model
        self.encoder = SentenceTransformer(embedding_model)

        # Load bottleneck definitions
        self.bottleneck_data = load_bottlenecks()

        # Create reference embeddings for bottlenecks
        self._create_reference_embeddings()

    def _create_reference_embeddings(self):
        """
        Create unit-normalized embeddings for all bottlenecks (reference side).
        """
        reference_texts: List[str] = []
        self.reference_map = {}

        # Add bottleneck descriptions
        for challenge_id, challenge in self.bottleneck_data["challenges"].items():
            for bottleneck in challenge["bottlenecks"]:
                text = f"{bottleneck['name']}. {bottleneck['description']}"
                reference_texts.append(text)
                self.reference_map[len(reference_texts) - 1] = {
                    "type": "bottleneck",
                    "id": bottleneck["id"],
                    "name": bottleneck["name"],
                    "challenge_id": challenge_id,
                }

        if not reference_texts:
            self.reference_embeddings = np.empty((0, 0), dtype=self.dtype)
            print("[PreFilter] No reference texts found.")
            return

        # Encode & normalize → cosine = dot product
        ref_emb = self.encoder.encode(
            reference_texts,
            batch_size=self.encode_batch_size,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        ).astype(self.dtype, copy=False)

        ref_emb = _l2_normalize(ref_emb).astype(self.dtype, copy=False)
        # Keep contiguous for fast BLAS
        self.reference_embeddings = np.ascontiguousarray(ref_emb)
        print(f"[PreFilter] Created {len(self.reference_embeddings)} normalized reference embeddings")

    def filter(self, chunk_text: str):
        """
        Filter a single chunk using cosine similarity vs. precomputed references.
        Returns (is_relevant, hints) tuple where is_relevant is True if max similarity ≥ threshold.
        """
        if not chunk_text or self.reference_embeddings.size == 0:
            return False, []

        # 1×D normalized text embedding
        text_emb = self.encoder.encode(
            [chunk_text],
            batch_size=self.encode_batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype(self.dtype, copy=False)
        text_emb = _l2_normalize(text_emb).astype(self.dtype, copy=False)  # shape (1, D)

        # Cosine via dot product (M,) ← (M,D) @ (D,)
        sims = self.reference_embeddings @ text_emb[0]
        max_sim = float(sims.max())
        is_relevant = max_sim >= self.embedding_threshold
        
        # Generate hints about top matching references
        hints = []
        if is_relevant:
            top_idx = sims.argmax()
            hints.append(f"Similarity: {max_sim:.3f}")
        
        return is_relevant, hints

    def filter_batch(self, chunk_texts: List[str]):
        """
        Filter multiple chunks at once (vectorized).
        Returns a list of (is_relevant, hints) tuples for each input text.
        """
        if not chunk_texts:
            return []

        if self.reference_embeddings.size == 0:
            return [(False, []) for _ in chunk_texts]

        # N×D normalized text embeddings
        text_embs = self.encoder.encode(
            chunk_texts,
            batch_size=self.encode_batch_size,
            convert_to_numpy=True,
            show_progress_bar=self.show_progress,
        ).astype(self.dtype, copy=False)
        text_embs = _l2_normalize(text_embs).astype(self.dtype, copy=False)
        text_embs = np.ascontiguousarray(text_embs)

        # N×M similarities via single GEMM
        sim_matrix = text_embs @ self.reference_embeddings.T  # (N, M)
        max_sims = sim_matrix.max(axis=1)
        thr = self.embedding_threshold
        
        # Build results with hints
        results = []
        for max_sim in max_sims:
            is_relevant = bool(max_sim >= thr)
            hints = []
            if is_relevant:
                hints.append(f"Similarity: {float(max_sim):.3f}")
            results.append((is_relevant, hints))
        
        return results

    def max_similarity(self, chunk_text: str) -> float:
        """Return the max cosine similarity (helps with threshold calibration)."""
        if not chunk_text or self.reference_embeddings.size == 0:
            return 0.0
        text_emb = self.encoder.encode(
            [chunk_text], convert_to_numpy=True, show_progress_bar=False
        ).astype(self.dtype, copy=False)
        text_emb = _l2_normalize(text_emb).astype(self.dtype, copy=False)
        sims = self.reference_embeddings @ text_emb[0]
        return float(sims.max())


