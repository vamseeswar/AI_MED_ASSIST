from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.audit import AuditLog
from backend.app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from backend.app.services.auth_service import get_current_user
from rag.pipelines.rag_pipeline import get_rag_pipeline
from rag.retrieval.vector_store import get_vector_store
from rag.retrieval.keyword_index import get_keyword_index
from rag.embeddings.embedding_provider import get_embedding_provider

router = APIRouter(prefix="/search", tags=["Search & Retrieval"])


@router.post("", response_model=SearchResponse)
def search_documents(
    search_req: SearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes semantic, keyword, or hybrid search across indexed medical documents."""
    rag_pipe = get_rag_pipeline()
    doc_id = search_req.document_id

    # If document_id provided, verify ownership or admin role
    if doc_id:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc or (current_user.role != "ADMIN" and doc.user_id != current_user.id):
            return SearchResponse(
                query=search_req.query,
                search_type=search_req.search_type,
                total_results=0,
                results=[]
            )

    results_data = []

    if search_req.search_type == "semantic":
        # Pure dense vector search
        emb_provider = get_embedding_provider()
        q_vec = emb_provider.embed_query(search_req.query)
        v_store = get_vector_store()
        raw_results = v_store.search(q_vec, top_k=search_req.top_k, document_id=doc_id)
        for r in raw_results:
            results_data.append(SearchResultItem(
                document_id=r.get("document_id"),
                document_name=r.get("document_name", "Medical Document"),
                page_number=r.get("page_number", 1),
                section_heading=r.get("section_heading", "General"),
                snippet=r.get("content", "")[:300],
                relevance_score=r.get("vector_score", 0.0)
            ))

    elif search_req.search_type == "keyword":
        # Pure BM25 keyword search
        kw_idx = get_keyword_index()
        raw_results = kw_idx.search(search_req.query, top_k=search_req.top_k, document_id=doc_id)
        for r in raw_results:
            results_data.append(SearchResultItem(
                document_id=r.get("document_id"),
                document_name=r.get("document_name", "Medical Document"),
                page_number=r.get("page_number", 1),
                section_heading=r.get("section_heading", "General"),
                snippet=r.get("content", "")[:300],
                relevance_score=r.get("bm25_score", 0.0)
            ))

    else:
        # Default: Hybrid search (RRF + Reranker)
        rag_res = rag_pipe.retrieve(search_req.query, top_k=search_req.top_k, document_id=doc_id)
        for c in rag_res["chunks"]:
            score = c.get("rerank_score") or c.get("relevance_score") or c.get("vector_score") or 0.0
            results_data.append(SearchResultItem(
                document_id=c.get("document_id"),
                document_name=c.get("document_name", "Medical Document"),
                page_number=c.get("page_number", 1),
                section_heading=c.get("section_heading", "General"),
                snippet=c.get("content", "")[:300],
                relevance_score=round(float(score), 3)
            ))

    # Audit logging
    ip = request.client.host if request.client else None
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_SEARCH",
        resource_type="SEARCH",
        resource_id=doc_id or "all_docs",
        details=f"Type: {search_req.search_type}, Query: '{search_req.query[:80]}', Found: {len(results_data)}",
        ip_address=ip,
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()

    return SearchResponse(
        query=search_req.query,
        search_type=search_req.search_type,
        total_results=len(results_data),
        results=results_data
    )
