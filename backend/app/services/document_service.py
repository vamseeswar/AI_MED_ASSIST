import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import app_logger
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.models.job import ProcessingJob
from backend.app.models.audit import AuditLog
from backend.app.utils.file_utils import (
    validate_file_upload,
    sanitize_filename,
    calculate_file_hash,
    get_safe_storage_path
)
from rag.loaders.pdf_loader import extract_pdf
from rag.loaders.docx_loader import extract_docx
from rag.loaders.txt_loader import extract_txt
from rag.loaders.csv_loader import extract_csv
from rag.processors.cleaner import clean_text
from rag.processors.extractor import extract_metadata_from_sections
from rag.pipelines.rag_pipeline import get_rag_pipeline


def save_and_create_document(db: Session, user: User, file: UploadFile, ip_address: Optional[str] = None) -> Document:
    """Saves file to disk safely, records DB entry, and initiates processing."""
    try:
        content = file.file.read()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file.")

    raw_filename = file.filename or "medical_doc.txt"
    extension, size_bytes = validate_file_upload(raw_filename, content, file.content_type or "")
    file_hash = calculate_file_hash(content)

    doc_id = str(uuid.uuid4())
    stored_filename = f"{doc_id}_{sanitize_filename(raw_filename)}"
    safe_path = get_safe_storage_path(stored_filename)

    # Write file to disk
    with open(safe_path, "wb") as f:
        f.write(content)

    # Create Document record
    document = Document(
        id=doc_id,
        user_id=user.id,
        filename=sanitize_filename(raw_filename),
        stored_filename=stored_filename,
        file_type=extension,
        file_size_bytes=size_bytes,
        file_hash=file_hash,
        status="QUEUED",
        page_count=0
    )
    db.add(document)

    # Create Initial Processing Job
    job = ProcessingJob(
        document_id=doc_id,
        job_type="DOCUMENT_INGESTION",
        status="QUEUED",
        progress_percent=0,
        started_at=datetime.now(timezone.utc)
    )
    db.add(job)

    # Audit Log
    audit = AuditLog(
        user_id=user.id,
        action="DOCUMENT_UPLOAD",
        resource_type="DOCUMENT",
        resource_id=doc_id,
        details=f"File: {document.filename} ({size_bytes} bytes)",
        ip_address=ip_address,
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()
    db.refresh(document)

    app_logger.info(f"Document {document.id} ({document.filename}) uploaded by user {user.email}")
    return document


def process_document(db: Session, document_id: str):
    """Executes the extraction, cleaning, chunking, and RAG indexing pipeline."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        app_logger.error(f"Cannot process: Document {document_id} not found in database.")
        return

    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
    file_path = get_safe_storage_path(document.stored_filename)

    try:
        # Step 1: Update status to PROCESSING
        document.status = "PROCESSING"
        if job:
            job.status = "PROCESSING"
            job.progress_percent = 20
        db.commit()

        # Step 2: Extract text based on file format
        ext = document.file_type.lower()
        if ext == "pdf":
            raw_sections = extract_pdf(file_path)
        elif ext == "docx":
            raw_sections = extract_docx(file_path)
        elif ext == "txt":
            raw_sections = extract_txt(file_path)
        elif ext == "csv":
            raw_sections = extract_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        # Step 3: Clean extracted text
        cleaned_sections = []
        for s in raw_sections:
            c_text = clean_text(s.get("content", ""))
            if c_text:
                s["content"] = c_text
                cleaned_sections.append(s)

        if not cleaned_sections:
            raise ValueError("No text could be extracted from this document.")

        if job:
            job.progress_percent = 45
        db.commit()

        # Step 4: Metadata extraction
        metadata = extract_metadata_from_sections(cleaned_sections, document.filename)
        document.title = metadata.get("title", document.filename)
        document.page_count = len(cleaned_sections)
        document.doc_metadata = json.dumps(metadata)

        # Step 5: Indexing in RAG Pipeline (Chunking, Embeddings, Vector Store, BM25)
        rag_pipeline = get_rag_pipeline()
        indexed_chunks = rag_pipeline.index_document_sections(
            document_id=document.id,
            document_name=document.filename,
            sections=cleaned_sections
        )

        if job:
            job.progress_percent = 80
        db.commit()

        # Step 6: Store Chunks in DB
        for c in indexed_chunks:
            chunk_rec = DocumentChunk(
                document_id=document.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                cleaned_content=c["cleaned_content"],
                page_number=c.get("page_number", 1),
                section_heading=c.get("section_heading", "General"),
                token_count=c.get("token_count", 0),
                chunk_metadata=json.dumps(c.get("metadata", {}))
            )
            db.add(chunk_rec)

        # Step 7: Rule-based / Initial Document Classification
        name_lower = document.filename.lower()
        full_text = " ".join([s["content"] for s in cleaned_sections[:5]]).lower()
        if "lab" in name_lower or "lab" in full_text or "cholesterol" in full_text or "test result" in full_text or "reference range" in full_text:
            document.category = "laboratory_report"
        elif "insurance" in name_lower or "insurance" in full_text or "claim" in full_text or "policy" in full_text:
            document.category = "insurance_document"
        elif "research" in name_lower or "abstract" in full_text or "methodology" in full_text or "journal" in full_text or "doi:" in full_text:
            document.category = "medical_research"
        elif "patient" in full_text or "clinical" in full_text or "hospital" in full_text:
            document.category = "clinical_report"
        else:
            document.category = "general_health_information"

        # Summary generation (First 2 sentences or clean lead)
        first_content = cleaned_sections[0]["content"].strip()
        summary_sentences = first_content.split(". ")[:2]
        document.summary = ". ".join(summary_sentences) + "." if summary_sentences else "Document successfully indexed."

        # Mark COMPLETED
        document.status = "COMPLETED"
        if job:
            job.status = "COMPLETED"
            job.progress_percent = 100
            job.completed_at = datetime.now(timezone.utc)
        db.commit()

        app_logger.info(f"Document {document_id} processed successfully: {len(indexed_chunks)} chunks indexed.")

    except Exception as exc:
        app_logger.error(f"Error processing document {document_id}: {exc}")
        document.status = "FAILED"
        document.error_message = str(exc)
        if job:
            job.status = "FAILED"
            job.error_message = str(exc)
        db.commit()


def get_user_documents(db: Session, user: User) -> List[Document]:
    """Retrieves all documents accessible by the user (admins see all, users see their own)."""
    if user.role == "ADMIN":
        return db.query(Document).order_by(Document.created_at.desc()).all()
    return db.query(Document).filter(Document.user_id == user.id).order_by(Document.created_at.desc()).all()


def get_document_by_id(db: Session, document_id: str, user: User) -> Document:
    """Retrieves a single document with authorization check."""
    query = db.query(Document).filter(Document.id == document_id)
    if user.role != "ADMIN":
        query = query.filter(Document.user_id == user.id)
    doc = query.first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc


def delete_document(db: Session, document_id: str, user: User, ip_address: Optional[str] = None):
    """Deletes a document from DB, disk, and vector indexes."""
    doc = get_document_by_id(db, document_id, user)

    # Remove from RAG index
    rag_pipeline = get_rag_pipeline()
    rag_pipeline.delete_document_index(document_id)

    # Remove physical file
    try:
        file_path = get_safe_storage_path(doc.stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as exc:
        app_logger.warning(f"Error removing file from disk: {exc}")

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="DOCUMENT_DELETE",
        resource_type="DOCUMENT",
        resource_id=doc.id,
        details=f"Deleted file {doc.filename}",
        ip_address=ip_address,
        status="SUCCESS"
    )
    db.add(audit)

    # Delete from DB
    db.delete(doc)
    db.commit()
    app_logger.info(f"Document {document_id} deleted by user {user.email}")
    return {"message": "Document deleted successfully."}
