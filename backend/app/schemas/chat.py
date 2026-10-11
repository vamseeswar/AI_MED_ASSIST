from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None


class CitationSchema(BaseModel):
    document_id: Optional[str] = None
    document_name: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    snippet: str
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: List[CitationSchema] = []
    sources: List[CitationSchema] = []
    agent: str
    processing_time: float


class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    agent_type: Optional[str] = None
    created_at: datetime
    citations: List[CitationSchema] = []


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
