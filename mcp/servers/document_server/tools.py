from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from mcp.registry import mcp_registry
from rag.pipelines.rag_pipeline import get_rag_pipeline
from backend.app.core.database import SessionLocal
from backend.app.models.document import Document


class SearchDocumentsParams(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(5, ge=1, le=20)
    document_id: Optional[str] = None


def search_documents_tool(query: str, top_k: int = 5, document_id: Optional[str] = None, user_context: Optional[Dict[str, Any]] = None):
    pipeline = get_rag_pipeline()
    retrieval = pipeline.retrieve(query=query, top_k=top_k, document_id=document_id)
    return {
        "query": query,
        "count": retrieval["chunks_retrieved_count"],
        "citations": retrieval["citations"],
        "snippets": [
            {
                "document_name": c.get("document_name"),
                "page": c.get("page_number"),
                "heading": c.get("section_heading"),
                "text": c.get("content")[:250]
            }
            for c in retrieval["chunks"]
        ]
    }


class GetDocumentParams(BaseModel):
    document_id: str


def get_document_tool(document_id: str, user_context: Optional[Dict[str, Any]] = None):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID '{document_id}' not found.")
        return {
            "id": doc.id,
            "filename": doc.filename,
            "title": doc.title,
            "file_type": doc.file_type,
            "page_count": doc.page_count,
            "category": doc.category,
            "summary": doc.summary
        }
    finally:
        db.close()


class GetDocumentSectionParams(BaseModel):
    document_id: str
    section_index: int = Field(..., ge=0)


def get_document_section_tool(document_id: str, section_index: int, user_context: Optional[Dict[str, Any]] = None):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID '{document_id}' not found.")
        chunks = doc.chunks
        if section_index >= len(chunks):
            raise ValueError(f"Section index {section_index} out of range (document has {len(chunks)} sections).")
        chunk = chunks[section_index]
        return {
            "document_id": doc.id,
            "section_index": section_index,
            "page_number": chunk.page_number,
            "heading": chunk.section_heading,
            "content": chunk.content
        }
    finally:
        db.close()


class SummarizeDocumentParams(BaseModel):
    document_id: str


def summarize_document_tool(document_id: str, user_context: Optional[Dict[str, Any]] = None):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID '{document_id}' not found.")
        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "title": doc.title,
            "summary": doc.summary or "Summary not yet generated."
        }
    finally:
        db.close()


def register_document_server_tools():
    mcp_registry.register_tool(
        name="search_documents",
        server="document_server",
        description="Search indexed documents using hybrid semantic and BM25 retrieval.",
        func=search_documents_tool,
        param_model=SearchDocumentsParams,
        read_only=True
    )
    mcp_registry.register_tool(
        name="get_document",
        server="document_server",
        description="Retrieve document metadata and summary by ID.",
        func=get_document_tool,
        param_model=GetDocumentParams,
        read_only=True
    )
    mcp_registry.register_tool(
        name="get_document_section",
        server="document_server",
        description="Fetch a specific section or chunk from a document.",
        func=get_document_section_tool,
        param_model=GetDocumentSectionParams,
        read_only=True
    )
    mcp_registry.register_tool(
        name="summarize_document",
        server="document_server",
        description="Retrieve or generate a summary of an indexed document.",
        func=summarize_document_tool,
        param_model=SummarizeDocumentParams,
        read_only=True
    )


register_document_server_tools()
