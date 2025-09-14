# utils.py
from typing import Optional, Tuple
import re
import numpy as np
from typing import Dict, List, Optional, Tuple
from sentence_transformers import SentenceTransformer
from bottleneck_definitions import load_bottlenecks

# Simple module-level caches
_ENCODER_CACHE: Dict[str, SentenceTransformer] = {}
_CHALLENGE_EMB_CACHE: Dict[Tuple[str, int], Tuple[np.ndarray, List[Dict]]] = {}
# key: (embedding_model, challenge_id) -> (emb_matrix [M,D] L2-normalized, meta list)

def _get_encoder(model_name: str) -> SentenceTransformer:
    enc = _ENCODER_CACHE.get(model_name)
    if enc is None:
        enc = SentenceTransformer(model_name)
        _ENCODER_CACHE[model_name] = enc
    return enc

def _l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if x.ndim == 1:
        x = x[None, :]
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(norms, eps)

def _challenge_index(
    challenge_id: int,
    *,
    embedding_model: str = "all-mpnet-base-v2",
    dtype=np.float32,
    show_progress: bool = False,
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Build (or fetch from cache) the L2-normalized embedding matrix for all
    bottlenecks under the given challenge, plus their metadata list.
    """
    key = (embedding_model, int(challenge_id))
    cached = _CHALLENGE_EMB_CACHE.get(key)
    if cached is not None:
        return cached

    data = load_bottlenecks()
    if int(challenge_id) not in data["challenges"]:
        raise ValueError(f"Unknown challenge_id: {challenge_id}")

    # texts & metadata for this challenge's bottlenecks
    ch = data["challenges"][int(challenge_id)]
    texts: List[str] = []
    meta: List[Dict] = []
    for b in ch["bottlenecks"]:
        texts.append(f"{b['name']}. {b['description']}")
        meta.append({"bottleneck_id": b["id"], "name": b["name"]})

    if not texts:
        emb = np.empty((0, 0), dtype=dtype)
        _CHALLENGE_EMB_CACHE[key] = (emb, meta)
        return emb, meta

    encoder = _get_encoder(embedding_model)
    ref = encoder.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=show_progress,
    ).astype(dtype, copy=False)
    ref = _l2_normalize(ref).astype(dtype, copy=False)
    ref = np.ascontiguousarray(ref)
    _CHALLENGE_EMB_CACHE[key] = (ref, meta)
    return ref, meta

def bottleneck_similarity_for_challenge(
    evidence_span: str,
    challenge_id: int | str,
    *,
    embedding_model: str = "all-mpnet-base-v2",
    show_progress: bool = False,
) -> List[Dict]:
    """
    Compute cosine similarity between the evidence span and ALL bottlenecks
    under the given challenge. Returns a list sorted by cosine desc.

    Returns each item as:
      {
        "bottleneck_id": str,
        "name": str,
        "cosine": float,           # ∈ [-1, 1] (usually [0, 1] for these models)
        "cosine_distance": float   # = 1 - cosine
      }
    """
    if not evidence_span or not str(evidence_span).strip():
        return []

    ch_id = int(challenge_id)
    ref_emb, meta = _challenge_index(
        ch_id, embedding_model=embedding_model, show_progress=show_progress
    )
    if ref_emb.size == 0:
        return []

    # Encode + normalize the query text (evidence span)
    encoder = _get_encoder(embedding_model)
    q = encoder.encode(
        [evidence_span],
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(ref_emb.dtype, copy=False)
    q = _l2_normalize(q).astype(ref_emb.dtype, copy=False)

    # Cosine via dot product (M,) ← (M,D) @ (D,)
    sims = ref_emb @ q[0]  # shape (M,)

    results = []
    for i, m in enumerate(meta):
        c = float(sims[i])
        results.append({
            "bottleneck_id": m["bottleneck_id"],
            "name": m["name"],
            "cosine": c,
            "cosine_distance": float(1.0 - c),
        })

    # Sort by cosine descending
    results.sort(key=lambda r: r["cosine"], reverse=True)
    return results

def clear_embedding_caches() -> None:
    """Optional helper: clear cached encoder and per-challenge refs (for testing)."""
    _ENCODER_CACHE.clear()
    _CHALLENGE_EMB_CACHE.clear()

_WHITESPACE_RE = re.compile(r"\s+", flags=re.MULTILINE)

def normalize_ws(s: str) -> str:
    """Collapse all whitespace to single spaces and trim."""
    return _WHITESPACE_RE.sub(" ", s).strip()

def find_verbatim_with_offsets(quote: str, text: str) -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    Whitespace-tolerant verbatim check.
    Returns (found?, (start, end)) in the ORIGINAL text when we can map it; else (True, None).
    """
    if not quote or not text:
        return False, None

    # Fast path: exact substring → reliable offsets
    start = text.find(quote)
    if start >= 0:
        return True, (start, start + len(quote))

    # Normalized containment (handles line breaks, multiple spaces, etc.)
    norm_q = normalize_ws(quote)
    norm_t = normalize_ws(text)
    if norm_q not in norm_t:
        return False, None

    # Best-effort offset mapping using leading/trailing probes
    lead = norm_q[:8]
    trail = norm_q[-8:] if len(norm_q) >= 8 else norm_q
    start = text.find(lead)
    if start < 0:
        return True, None
    end = text.find(trail, start)
    end = (start + len(quote)) if end < 0 else end + len(trail)
    return True, (start, end)
