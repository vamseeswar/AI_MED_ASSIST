import time
import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db, SessionLocal
from backend.app.models.user import User
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.citation import Citation
from backend.app.models.audit import AuditLog
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationSchema,
    ConversationResponse,
    MessageSchema
)
from backend.app.services.auth_service import get_current_user
from agents.graph.orchestrator import run_agent_workflow
from ai.llm_provider import get_llm_client
from rag.citations.citation_engine import format_citations_markdown
from agents.prompts.agent_prompts import CORE_MEDICAL_DISCLAIMER, SYSTEM_PROMPT_RAG_AGENT
from backend.app.core.logging import app_logger

router = APIRouter(prefix="/chat", tags=["Conversational AI & Streaming"])


@router.post("", response_model=ChatResponse)
def chat_sync(
    chat_req: ChatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Synchronous chat endpoint executing the LangGraph multi-agent RAG workflow."""
    start_time = time.time()

    # 1. Resolve or Create Conversation
    conversation = None
    if chat_req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_req.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conversation:
        title = chat_req.message[:50].strip() or "Medical Consultation"
        conversation = Conversation(
            user_id=current_user.id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Persist User Message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_req.message
    )
    db.add(user_msg)
    db.commit()

    # 3. Fetch recent history
    history_records = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.desc()).limit(6).all()

    formatted_history = [
        {"role": m.role, "content": m.content}
        for m in reversed(history_records)
    ]

    # 4. Execute LangGraph multi-agent workflow
    workflow_res = run_agent_workflow(
        query=chat_req.message,
        document_id=chat_req.document_id,
        conversation_id=conversation.id,
        history=formatted_history
    )

    elapsed_time = round(time.time() - start_time, 3)
    final_answer = workflow_res.get("final_answer", "")
    citations_data = workflow_res.get("citations", [])
    agent_name = workflow_res.get("agent_provenance", "Document Agent")

    # 5. Persist Assistant Message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=final_answer,
        agent_type=agent_name,
        latency_ms=elapsed_time * 1000
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # 6. Persist Citations
    saved_citations = []
    for c in citations_data:
        cit_rec = Citation(
            message_id=assistant_msg.id,
            document_id=c.get("document_id"),
            document_name=c.get("document_name", "Medical Reference"),
            page_number=c.get("page_number"),
            section_heading=c.get("section_heading"),
            snippet=c.get("snippet", ""),
            relevance_score=c.get("relevance_score")
        )
        db.add(cit_rec)
        saved_citations.append(CitationSchema(
            document_id=c.get("document_id"),
            document_name=c.get("document_name", "Medical Reference"),
            page_number=c.get("page_number"),
            section_heading=c.get("section_heading"),
            snippet=c.get("snippet", ""),
            relevance_score=c.get("relevance_score")
        ))
    db.commit()

    # Audit log
    ip = request.client.host if request.client else None
    audit = AuditLog(
        user_id=current_user.id,
        action="CHAT_QUERY",
        resource_type="CONVERSATION",
        resource_id=conversation.id,
        details=f"Agent: {agent_name}, Citations: {len(saved_citations)}, Latency: {elapsed_time}s",
        ip_address=ip,
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=final_answer,
        citations=saved_citations,
        sources=saved_citations,
        agent=agent_name,
        processing_time=elapsed_time
    )


@router.post("/stream")
def chat_streaming_sse(
    chat_req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Server-Sent Events (SSE) streaming endpoint for real-time progressive response tokens."""
    # Resolve or create conversation
    conversation = None
    if chat_req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_req.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            title=chat_req.message[:50].strip() or "Medical Consultation"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Persist User Message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_req.message
    )
    db.add(user_msg)
    db.commit()

    # Run initial workflow to obtain intent, safety, context, and citations
    workflow_res = run_agent_workflow(
        query=chat_req.message,
        document_id=chat_req.document_id,
        conversation_id=conversation.id
    )

    final_answer = workflow_res.get("final_answer", "")
    citations = workflow_res.get("citations", [])
    agent_name = workflow_res.get("agent_provenance", "Document Agent")

    def event_generator():
        # 1. Send conversation metadata
        meta_event = {
            "type": "metadata",
            "conversation_id": conversation.id,
            "agent": agent_name,
            "citations": citations
        }
        yield f"data: {json.dumps(meta_event)}\n\n"

        # 2. Stream answer text chunk-by-chunk
        words = final_answer.split()
        for idx in range(0, len(words), 3):
            token_chunk = " ".join(words[idx:idx + 3]) + " "
            event = {
                "type": "token",
                "content": token_chunk
            }
            yield f"data: {json.dumps(event)}\n\n"
            time.sleep(0.02)  # Micro delay for realistic SSE progressive rendering

        # 3. Send done event
        done_event = {"type": "done", "conversation_id": conversation.id}
        yield f"data: {json.dumps(done_event)}\n\n"

        # Save assistant message to DB
        local_db = SessionLocal()
        try:
            asst_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=final_answer,
                agent_type=agent_name
            )
            local_db.add(asst_msg)
            local_db.commit()
            local_db.refresh(asst_msg)

            for c in citations:
                cit_rec = Citation(
                    message_id=asst_msg.id,
                    document_id=c.get("document_id"),
                    document_name=c.get("document_name", "Medical Reference"),
                    page_number=c.get("page_number"),
                    section_heading=c.get("section_heading"),
                    snippet=c.get("snippet", ""),
                    relevance_score=c.get("relevance_score")
                )
                local_db.add(cit_rec)
            local_db.commit()
        finally:
            local_db.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all conversation threads for the user."""
    convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=len(c.messages)
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation_detail(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches complete message history and citations for a conversation thread."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    messages_data = []
    for m in conv.messages:
        citations_data = [
            CitationSchema(
                document_id=c.document_id,
                document_name=c.document_name,
                page_number=c.page_number,
                section_heading=c.section_heading,
                snippet=c.snippet,
                relevance_score=c.relevance_score
            )
            for c in m.citations
        ]
        messages_data.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "agent_type": m.agent_type,
            "created_at": m.created_at,
            "citations": citations_data
        })

    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
        "messages": messages_data
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a conversation thread and its associated message records."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation successfully deleted."}
