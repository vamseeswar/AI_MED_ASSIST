import os
import hashlib
import numpy as np
from typing import List
from backend.app.core.config import settings
from backend.app.core.logging import app_logger

# Cached singleton model instance
_ST_MODEL = None


class BaseEmbeddingProvider:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError


class FastDeterministicEmbeddingProvider(BaseEmbeddingProvider):
    """Fallback embedding provider generating deterministic 384-dimensional unit vectors."""
    def __init__(self, dim: int = 384):
        self.dim = dim

    def _hash_to_vector(self, text: str) -> List[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            tokens = ["empty"]
        for token in tokens:
            seed = int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16)
            np.random.seed(seed)
            component = np.random.normal(0, 1, self.dim)
            vec += component
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_to_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._hash_to_vector(text)


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        global _ST_MODEL
        self.model_name = model_name
        self.fallback = FastDeterministicEmbeddingProvider(dim=384)
        if _ST_MODEL is None:
            try:
                from sentence_transformers import SentenceTransformer
                app_logger.info(f"Loading SentenceTransformer: {model_name}...")
                _ST_MODEL = SentenceTransformer(model_name)
                app_logger.info("SentenceTransformer loaded successfully.")
            except Exception as exc:
                app_logger.warning(f"Could not load SentenceTransformer '{model_name}': {exc}. Using deterministic vector fallback.")
                _ST_MODEL = "FALLBACK"
        self.model = _ST_MODEL

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.model == "FALLBACK" or self.model is None:
            return self.fallback.embed_documents(texts)
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as exc:
            app_logger.warning(f"SentenceTransformer encoding error: {exc}. Falling back to deterministic vectors.")
            return self.fallback.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Factory for embedding provider based on application configuration."""
    provider_name = settings.EMBEDDING_PROVIDER.lower()

    if provider_name == "mock":
        return FastDeterministicEmbeddingProvider()
    elif provider_name == "sentence-transformers":
        return SentenceTransformerEmbeddingProvider(settings.EMBEDDING_MODEL)
    else:
        # Default to SentenceTransformer with fallback
        return SentenceTransformerEmbeddingProvider()
