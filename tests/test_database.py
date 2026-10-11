import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base, check_db_connectivity
from backend.app.models import (
    User, Document, DocumentChunk, Conversation,
    Message, Citation, ProcessingJob, AuditLog
)

from backend.app.core.database import SessionLocal, engine


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_db_connectivity():
    assert check_db_connectivity() is True


def test_create_user_and_document_cascade(db_session):
    # 1. Create User
    user = User(
        email="test_doctor@medassist.ai",
        hashed_password="hashed_secure_password_123",
        full_name="Dr. Jane Smith",
        role="ADMIN"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.role == "ADMIN"

    # 2. Create Document for User
    doc = Document(
        user_id=user.id,
        filename="cardiology_study.pdf",
        stored_filename="uuid_cardiology_study.pdf",
        file_type="pdf",
        file_size_bytes=1048576,
        file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status="COMPLETED",
        page_count=5
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    assert doc.id is not None
    assert doc.user_id == user.id

    # 3. Create Document Chunk
    chunk = DocumentChunk(
        document_id=doc.id,
        chunk_index=0,
        content="Patient presents with elevated blood pressure.",
        cleaned_content="patient presents with elevated blood pressure",
        page_number=1,
        section_heading="Clinical Findings"
    )
    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(chunk)

    assert chunk.id is not None
    assert chunk.document_id == doc.id

    # 4. Verify cascade deletion
    db_session.delete(user)
    db_session.commit()

    # User deleted -> document deleted -> chunk deleted
    assert db_session.query(Document).filter_by(id=doc.id).first() is None
    assert db_session.query(DocumentChunk).filter_by(id=chunk.id).first() is None


def test_conversation_message_citation_flow(db_session):
    user = User(email="patient_case@medassist.ai", hashed_password="pw")
    db_session.add(user)
    db_session.commit()

    conv = Conversation(user_id=user.id, title="Hypertension inquiry")
    db_session.add(conv)
    db_session.commit()

    msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content="According to the research paper, blood pressure metrics are categorized...",
        agent_type="RAG Agent",
        latency_ms=342.5
    )
    db_session.add(msg)
    db_session.commit()

    citation = Citation(
        message_id=msg.id,
        document_name="guidelines.pdf",
        page_number=3,
        section_heading="Guidelines Table",
        snippet="Stage 1 hypertension systolic 130-139 mm Hg",
        relevance_score=0.92
    )
    db_session.add(citation)
    db_session.commit()

    assert len(msg.citations) == 1
    assert msg.citations[0].document_name == "guidelines.pdf"
    assert msg.citations[0].relevance_score == 0.92


def test_job_and_audit_logging(db_session):
    user = User(email="audit_user@medassist.ai", hashed_password="pw")
    db_session.add(user)
    db_session.commit()

    audit = AuditLog(
        user_id=user.id,
        action="DOCUMENT_UPLOAD",
        resource_type="DOCUMENT",
        resource_id="doc-1234",
        details="Uploaded file lab_report.pdf (size: 204KB)",
        status="SUCCESS"
    )
    db_session.add(audit)
    db_session.commit()

    saved_audit = db_session.query(AuditLog).filter_by(user_id=user.id).first()
    assert saved_audit is not None
    assert saved_audit.action == "DOCUMENT_UPLOAD"
    assert saved_audit.status == "SUCCESS"
