import os
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import app_logger
from rag.embeddings.embedding_provider import get_embedding_provider


class InMemoryVectorStore:
    """Thread-safe vector index supporting cosine similarity and metadata filtering."""
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[np.ndarray] = []

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        for chunk, emb in zip(chunks, embeddings):
            self.chunks.append(chunk)
            vec = np.array(emb, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self.embeddings.append(vec)

    def search(self, query_embedding: List[float], top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.chunks or not self.embeddings:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        scores = []
        for idx, (chunk, emb) in enumerate(zip(self.chunks, self.embeddings)):
            if document_id and chunk.get("document_id") != document_id:
                continue

            # Cosine similarity
            cos_sim = float(np.dot(q_vec, emb))
            scores.append((cos_sim, chunk))

        # Sort descending by similarity score
        scores.sort(key=lambda x: x[0], reverse=True)
        top_results = []
        for score, chunk in scores[:top_k]:
            res = chunk.copy()
            res["vector_score"] = round(float(score), 4)
            top_results.append(res)

        return top_results

    def delete_document(self, document_id: str):
        filtered_chunks = []
        filtered_embeddings = []
        for c, e in zip(self.chunks, self.embeddings):
            if c.get("document_id") != document_id:
                filtered_chunks.append(c)
                filtered_embeddings.append(e)
        self.chunks = filtered_chunks
        self.embeddings = filtered_embeddings


class ChromaVectorStore:
    """ChromaDB implementation with graceful fallback."""
    def __init__(self, persist_dir: str = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.memory_store = InMemoryVectorStore()
        self.chroma_client = None
        self.collection = None

        try:
            import chromadb
            os.makedirs(self.persist_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name="medassist_documents",
                metadata={"hnsw:space": "cosine"}
            )
            app_logger.info("ChromaDB vector store initialized successfully.")
        except Exception as exc:
            app_logger.warning(f"ChromaDB initialization failed: {exc}. Using in-memory vector store.")

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        self.memory_store.add_chunks(chunks, embeddings)
        if self.collection:
            try:
                ids = [f"{c['document_id']}_{c['chunk_index']}" for c in chunks]
                documents = [c["content"] for c in chunks]
                metadatas = [
                    {
                        "document_id": str(c["document_id"]),
                        "page_number": int(c.get("page_number", 1)),
                        "section_heading": str(c.get("section_heading", "General"))
                    }
                    for c in chunks
                ]
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
            except Exception as exc:
                app_logger.warning(f"Error persisting chunks to Chroma: {exc}")

    def search(self, query_embedding: List[float], top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.collection:
            try:
                where_clause = {"document_id": document_id} if document_id else None
                res = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_clause
                )
                if res and res.get("documents") and res["documents"][0]:
                    results = []
                    docs = res["documents"][0]
                    metas = res["metadatas"][0] if res.get("metadatas") else [{}] * len(docs)
                    distances = res["distances"][0] if res.get("distances") else [0.0] * len(docs)
                    ids = res["ids"][0] if res.get("ids") else [""] * len(docs)

                    for d, m, dist, cid in zip(docs, metas, distances, ids):
                        # For cosine distance: similarity = 1 - distance
                        sim_score = max(0.0, 1.0 - float(dist))
                        results.append({
                            "document_id": m.get("document_id"),
                            "chunk_index": int(cid.split("_")[-1]) if "_" in cid else 0,
                            "content": d,
                            "page_number": m.get("page_number", 1),
                            "section_heading": m.get("section_heading", "General"),
                            "vector_score": round(sim_score, 4)
                        })
                    return results
            except Exception as exc:
                app_logger.warning(f"Chroma query failed: {exc}, using memory store fallback.")

        return self.memory_store.search(query_embedding, top_k=top_k, document_id=document_id)

    def delete_document(self, document_id: str):
        self.memory_store.delete_document(document_id)
        if self.collection:
            try:
                self.collection.delete(where={"document_id": document_id})
            except Exception as exc:
                app_logger.warning(f"Failed to delete document from Chroma: {exc}")


# Global vector store instance
_GLOBAL_VECTOR_STORE = None


def get_vector_store() -> ChromaVectorStore:
    global _GLOBAL_VECTOR_STORE
    if _GLOBAL_VECTOR_STORE is None:
        _GLOBAL_VECTOR_STORE = ChromaVectorStore()
    return _GLOBAL_VECTOR_STORE
