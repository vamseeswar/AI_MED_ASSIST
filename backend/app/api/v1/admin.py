"""
Admin and Observability API endpoints.
Provides system metrics, audit logs, and AI evaluation results.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.services.auth_service import get_current_user
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.job import ProcessingJob
from backend.app.models.audit import AuditLog
from ai.evaluation.runner import get_latest_evaluation, run_evaluation
from loguru import logger

router = APIRouter(prefix="/admin", tags=["Admin & Observability"])


@router.get("/metrics")
def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns live system observability metrics.
    Admin or authenticated users can view system health statistics.
    """
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_docs = db.query(func.count(Document.id)).scalar() or 0
    total_chunks = db.query(func.count(DocumentChunk.id)).scalar() or 0
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0
    total_messages = db.query(func.count(Message.id)).scalar() or 0
    total_audit_events = db.query(func.count(AuditLog.id)).scalar() or 0

    # Job status distribution
    job_statuses = (
        db.query(ProcessingJob.status, func.count(ProcessingJob.id))
        .group_by(ProcessingJob.status)
        .all()
    )
    job_breakdown = {status: count for status, count in job_statuses}

    # Recent audit actions
    action_counts = (
        db.query(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
        .order_by(func.count(AuditLog.id).desc())
        .limit(6)
        .all()
    )
    audit_breakdown = {action: count for action, count in action_counts}

    # Document type breakdown
    doc_types = (
        db.query(Document.file_type, func.count(Document.id))
        .group_by(Document.file_type)
        .all()
    )
    type_breakdown = {ft: count for ft, count in doc_types}

    return {
        "status": "healthy",
        "counts": {
            "users": total_users,
            "documents": total_docs,
            "chunks": total_chunks,
            "conversations": total_conversations,
            "messages": total_messages,
            "audit_logs": total_audit_events
        },
        "job_status_breakdown": job_breakdown,
        "audit_action_breakdown": audit_breakdown,
        "document_type_breakdown": type_breakdown
    }


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns paginated audit logs for system observability.
    """
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action)
    if status_filter:
        query = query.filter(AuditLog.status == status_filter)

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }


@router.get("/evaluation")
def get_evaluation_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieves the latest genuine RAG evaluation results.
    If evaluation has not been run, returns 'Not evaluated yet.' as per specification.
    """
    return get_latest_evaluation()


@router.post("/evaluation/run")
def trigger_evaluation_run(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Executes the benchmark evaluation runner and persists genuine metrics.
    """
    try:
        results = run_evaluation()
        return results
    except Exception as e:
        logger.error(f"Error during evaluation run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation execution failed: {str(e)}"
        )
