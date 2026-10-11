from typing import List, Dict, Any, Optional
from rag.chunking.splitter import MedicalTextSplitter
from rag.embeddings.embedding_provider import get_embedding_provider
from rag.retrieval.vector_store import get_vector_store
from rag.retrieval.keyword_index import get_keyword_index
from rag.retrieval.hybrid_search import hybrid_retrieve
from rag.reranking.reranker import get_reranker
from rag.citations.citation_engine import build_citations_from_retrieved_chunks
from backend.app.core.logging import app_logger


class RAGPipeline:
    def __init__(self):
        self.splitter = MedicalTextSplitter()
        self.embedding_provider = get_embedding_provider()
        self.vector_store = get_vector_store()
        self.keyword_index = get_keyword_index()
        self.reranker = get_reranker()

    def index_document_sections(self, document_id: str, document_name: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Splits document sections, computes embeddings, and indexes into dense vector store and BM25 index."""
        # 1. Chunking
        chunks = self.splitter.chunk_document_sections(sections, document_id=document_id)
        if not chunks:
            app_logger.warning(f"No chunks extracted from document {document_id}")
            return []

        # Tag chunks with document name
        for c in chunks:
            c["document_name"] = document_name

        # 2. Embeddings
        contents = [c["content"] for c in chunks]
        embeddings = self.embedding_provider.embed_documents(contents)

        # 3. Dense vector index
        self.vector_store.add_chunks(chunks, embeddings)

        # 4. Sparse BM25 keyword index
        self.keyword_index.add_chunks(chunks)

        app_logger.info(f"Successfully indexed {len(chunks)} chunks for document '{document_name}' ({document_id})")
        return chunks

    def retrieve(self, query: str, top_k: int = 5, document_id: Optional[str] = None) -> Dict[str, Any]:
        """Runs hybrid search, reranks context, and prepares citations."""
        # Hybrid retrieve
        candidate_chunks = hybrid_retrieve(query, top_k=top_k * 2, document_id=document_id)

        # Rerank
        reranked_chunks = self.reranker.rerank(query, candidate_chunks, top_k=top_k)

        # Build citations
        doc_names = {c.get("document_id"): c.get("document_name", "Medical Document") for c in reranked_chunks}
        citations = build_citations_from_retrieved_chunks(reranked_chunks, doc_name_lookup=doc_names)

        # Format context string for LLM injection
        context_blocks = []
        for idx, c in enumerate(reranked_chunks, start=1):
            doc = c.get("document_name", "Document")
            page = c.get("page_number", 1)
            heading = c.get("section_heading", "General")
            text = c.get("content", "").strip()
            context_blocks.append(f"[Source {idx} | {doc} | Page {page} | Section: {heading}]\n{text}")

        formatted_context = "\n\n---\n\n".join(context_blocks)

        return {
            "query": query,
            "chunks": reranked_chunks,
            "formatted_context": formatted_context,
            "citations": citations,
            "chunks_retrieved_count": len(reranked_chunks)
        }

    def delete_document_index(self, document_id: str):
        """Removes document chunks from both vector store and keyword index."""
        self.vector_store.delete_document(document_id)
        self.keyword_index.delete_document(document_id)
        app_logger.info(f"Deleted document index for {document_id}")


_GLOBAL_RAG_PIPELINE = None


def get_rag_pipeline() -> RAGPipeline:
    global _GLOBAL_RAG_PIPELINE
    if _GLOBAL_RAG_PIPELINE is None:
        _GLOBAL_RAG_PIPELINE = RAGPipeline()
    return _GLOBAL_RAG_PIPELINE
