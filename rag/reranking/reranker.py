import re
from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.core.logging import app_logger

# Cached reranker model
_RERANKER_MODEL = None


class ContextReranker:
    def __init__(self):
        global _RERANKER_MODEL
        self.enabled = settings.RERANKER_ENABLED
        self.cross_encoder = None

        if self.enabled and _RERANKER_MODEL is None:
            try:
                from sentence_transformers import CrossEncoder
                app_logger.info("Initializing CrossEncoder reranker (ms-marco-MiniLM-L-6-v2)...")
                _RERANKER_MODEL = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
                app_logger.info("CrossEncoder reranker loaded successfully.")
            except Exception as exc:
                app_logger.warning(f"CrossEncoder unavailable: {exc}. Using semantic term reranking fallback.")
                _RERANKER_MODEL = "FALLBACK"
        self.cross_encoder = _RERANKER_MODEL

    def _fallback_rerank(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Contextual term density and exact-phrase matching fallback."""
        q_tokens = set(re.findall(r'\b\w+\b', query.lower()))
        reranked = []

        for c in chunks:
            text = c.get("content", "").lower()
            overlap = sum(1 for tok in q_tokens if tok in text)
            exact_match_boost = 2.0 if query.lower() in text else 0.0
            base_score = float(c.get("relevance_score", 0.5))

            fused_score = base_score + (overlap * 0.1) + exact_match_boost
            c_copy = c.copy()
            c_copy["rerank_score"] = round(fused_score, 4)
            reranked.append(c_copy)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked

    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not chunks:
            return []

        if not self.enabled or self.cross_encoder == "FALLBACK" or self.cross_encoder is None:
            return self._fallback_rerank(query, chunks)[:top_k]

        try:
            pairs = [[query, c.get("content", "")] for c in chunks]
            scores = self.cross_encoder.predict(pairs)
            for idx, s in enumerate(scores):
                chunks[idx]["rerank_score"] = round(float(s), 4)
            chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
            return chunks[:top_k]
        except Exception as exc:
            app_logger.warning(f"CrossEncoder rerank execution failed: {exc}, using fallback.")
            return self._fallback_rerank(query, chunks)[:top_k]


_GLOBAL_RERANKER = None


def get_reranker() -> ContextReranker:
    global _GLOBAL_RERANKER
    if _GLOBAL_RERANKER is None:
        _GLOBAL_RERANKER = ContextReranker()
    return _GLOBAL_RERANKER
