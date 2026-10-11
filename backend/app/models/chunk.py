import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    cleaned_content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True, index=True)
    section_heading = Column(String(255), nullable=True)
    token_count = Column(Integer, default=0, nullable=False)
    embedding_id = Column(String(255), nullable=True, index=True)
    chunk_metadata = Column(Text, nullable=True)  # JSON-encoded metadata

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk doc={self.document_id} idx={self.chunk_index} page={self.page_number}>"
