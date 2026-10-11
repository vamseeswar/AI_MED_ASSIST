import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Request, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.job import ProcessingJob
from backend.app.schemas.document import DocumentResponse, DocumentStatusResponse, DocumentDetailResponse
from backend.app.services.auth_service import get_current_user
from backend.app.services.document_service import (
    save_and_create_document,
    process_document,
    get_user_documents,
    get_document_by_id,
    delete_document
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads a medical document (PDF, DOCX, TXT, CSV), validates, and kicks off ingestion."""
    ip = request.client.host if request.client else None
    document = save_and_create_document(db, current_user, file, ip_address=ip)

    # Process document synchronously or via background task
    # To ensure immediate availability in tests and rapid local dev, we execute processing
    process_document(db, document.id)
    db.refresh(document)

    return document


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all documents belonging to the authenticated user."""
    return get_user_documents(db, current_user)


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_details(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves detailed information, extracted metadata, and chunks for a document."""
    doc = get_document_by_id(db, document_id, current_user)
    meta = json.loads(doc.doc_metadata) if doc.doc_metadata else {}

    chunks_data = [
        {
            "id": c.id,
            "chunk_index": c.chunk_index,
            "page_number": c.page_number,
            "section_heading": c.section_heading,
            "token_count": c.token_count,
            "content": c.content[:300] + ("..." if len(c.content) > 300 else "")
        }
        for c in doc.chunks[:50]
    ]

    return DocumentDetailResponse(
        id=doc.id,
        user_id=doc.user_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        status=doc.status,
        error_message=doc.error_message,
        title=doc.title,
        page_count=doc.page_count,
        summary=doc.summary,
        category=doc.category,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        doc_metadata=meta,
        chunk_count=len(doc.chunks),
        chunks=chunks_data
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the current background processing state and progress percent."""
    doc = get_document_by_id(db, document_id, current_user)
    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()

    progress = job.progress_percent if job else (100 if doc.status == "COMPLETED" else 0)

    return DocumentStatusResponse(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        progress_percent=progress,
        error_message=doc.error_message,
        chunk_count=len(doc.chunks),
        updated_at=doc.updated_at
    )


@router.delete("/{document_id}")
def delete_document_endpoint(
    document_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a document and clears its vector and keyword embeddings."""
    ip = request.client.host if request.client else None
    return delete_document(db, document_id, current_user, ip_address=ip)
