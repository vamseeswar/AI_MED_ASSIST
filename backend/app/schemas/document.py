from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    error_message: Optional[str] = None
    title: Optional[str] = None
    page_count: int
    summary: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    id: str
    filename: str
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED
    progress_percent: int
    error_message: Optional[str] = None
    chunk_count: int = 0
    updated_at: datetime


class DocumentDetailResponse(DocumentResponse):
    doc_metadata: Optional[Dict[str, Any]] = None
    chunk_count: int = 0
    chunks: Optional[List[Dict[str, Any]]] = None
