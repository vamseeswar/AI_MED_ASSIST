from typing import List, Dict, Any, Optional
from rag.retrieval.vector_store import get_vector_store
from rag.retrieval.keyword_index import get_keyword_index
from rag.embeddings.embedding_provider import get_embedding_provider
from backend.app.core.logging import app_logger


def hybrid_retrieve(
    query: str,
    top_k: int = 5,
    document_id: Optional[str] = None,
    vector_weight: float = 0.6,
    keyword_weight: float = 0.4,
    rrf_k: int = 60
) -> List[Dict[str, Any]]:
    """Performs hybrid retrieval using Reciprocal Rank Fusion (RRF) between Dense Vector & BM25 Keyword searches."""
    embedding_provider = get_embedding_provider()
    vector_store = get_vector_store()
    keyword_index = get_keyword_index()

    # 1. Dense Vector Search
    query_vector = embedding_provider.embed_query(query)
    dense_results = vector_store.search(query_vector, top_k=top_k * 2, document_id=document_id)

    # 2. Sparse BM25 Keyword Search
    sparse_results = keyword_index.search(query, top_k=top_k * 2, document_id=document_id)

    # 3. Reciprocal Rank Fusion (RRF)
    chunk_scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}

    # Rank dense results
    for rank, item in enumerate(dense_results, start=1):
        key = f"{item.get('document_id')}_{item.get('chunk_index')}"
        chunk_map[key] = item
        score = vector_weight * (1.0 / (rrf_k + rank))
        chunk_scores[key] = chunk_scores.get(key, 0.0) + score

    # Rank sparse BM25 results
    for rank, item in enumerate(sparse_results, start=1):
        key = f"{item.get('document_id')}_{item.get('chunk_index')}"
        if key not in chunk_map:
            chunk_map[key] = item
        score = keyword_weight * (1.0 / (rrf_k + rank))
        chunk_scores[key] = chunk_scores.get(key, 0.0) + score

    # Sort candidates by combined RRF score
    sorted_items = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)

    final_results = []
    for key, rrf_score in sorted_items[:top_k]:
        item = chunk_map[key].copy()
        item["relevance_score"] = round(float(rrf_score * 100), 4)  # Normalized display score
        final_results.append(item)

    app_logger.debug(f"Hybrid retrieval for '{query[:40]}' returned {len(final_results)} chunks.")
    return final_results
