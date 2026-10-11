import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # LOGIN, LOGOUT, DOCUMENT_UPLOAD, RAG_QUERY, etc.
    resource_type = Column(String(100), nullable=True)  # DOCUMENT, CONVERSATION, MCP_TOOL, ML_MODEL
    resource_id = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)  # Safe details without credentials
    ip_address = Column(String(100), nullable=True)
    status = Column(String(50), default="SUCCESS", nullable=False)  # SUCCESS, FAILURE, BLOCKED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog action={self.action} user={self.user_id} status={self.status}>"
