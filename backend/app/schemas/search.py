from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    document_id: Optional[str] = None
    search_type: str = Field("hybrid", pattern="^(semantic|keyword|hybrid)$")
    top_k: int = Field(5, ge=1, le=20)


class SearchResultItem(BaseModel):
    document_id: Optional[str] = None
    document_name: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    snippet: str
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    search_type: str
    total_results: int
    results: List[SearchResultItem]
