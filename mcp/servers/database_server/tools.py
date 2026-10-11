import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from mcp.registry import mcp_registry
from backend.app.core.database import SessionLocal
from backend.app.models.document import Document
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message


class GetDocumentMetadataParams(BaseModel):
    document_id: str


def get_document_metadata_tool(document_id: str, user_context: Optional[Dict[str, Any]] = None):
    """READ-ONLY query for document metadata."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document '{document_id}' not found.")
        meta = json.loads(doc.doc_metadata) if doc.doc_metadata else {}
        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "title": doc.title,
            "file_type": doc.file_type,
            "file_size_bytes": doc.file_size_bytes,
            "page_count": doc.page_count,
            "status": doc.status,
            "category": doc.category,
            "metadata": meta,
            "created_at": str(doc.created_at)
        }
    finally:
        db.close()


class GetUserDocumentsParams(BaseModel):
    user_id: str


def get_user_documents_tool(user_id: str, user_context: Optional[Dict[str, Any]] = None):
    """READ-ONLY query for list of documents owned by a user."""
    # Enforce authorization if user_context is provided
    if user_context and user_context.get("role") != "ADMIN" and user_context.get("user_id") != user_id:
        raise PermissionError("Unauthorized access to requested user's documents.")

    db = SessionLocal()
    try:
        docs = db.query(Document).filter(Document.user_id == user_id).all()
        return [
            {
                "id": d.id,
                "filename": d.filename,
                "title": d.title,
                "file_type": d.file_type,
                "status": d.status,
                "category": d.category,
                "created_at": str(d.created_at)
            }
            for d in docs
        ]
    finally:
        db.close()


class GetConversationHistoryParams(BaseModel):
    conversation_id: str


def get_conversation_history_tool(conversation_id: str, user_context: Optional[Dict[str, Any]] = None):
    """READ-ONLY query for conversation message history."""
    db = SessionLocal()
    try:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        # Enforce authorization
        if user_context and user_context.get("role") != "ADMIN" and user_context.get("user_id") != conv.user_id:
            raise PermissionError("Unauthorized access to requested conversation.")

        messages = [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "agent_type": m.agent_type,
                "created_at": str(m.created_at)
            }
            for m in conv.messages
        ]
        return {
            "conversation_id": conv.id,
            "title": conv.title,
            "messages": messages
        }
    finally:
        db.close()


def register_database_server_tools():
    mcp_registry.register_tool(
        name="get_document_metadata",
        server="database_server",
        description="READ-ONLY query to fetch document technical and parsing metadata.",
        func=get_document_metadata_tool,
        param_model=GetDocumentMetadataParams,
        read_only=True
    )
    mcp_registry.register_tool(
        name="get_user_documents",
        server="database_server",
        description="READ-ONLY query to list documents associated with an account.",
        func=get_user_documents_tool,
        param_model=GetUserDocumentsParams,
        read_only=True
    )
    mcp_registry.register_tool(
        name="get_conversation_history",
        server="database_server",
        description="READ-ONLY query to fetch message history for a consultation thread.",
        func=get_conversation_history_tool,
        param_model=GetConversationHistoryParams,
        read_only=True
    )


register_database_server_tools()
