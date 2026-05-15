# schemas/document.py — Pydantic models for document-related API data

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentCreate(BaseModel):
    filename: str
    
    content: str


class AnalysisResultResponse(BaseModel):
    id: int
    summary: Optional[str] = None
    
    keywords: Optional[List[str]] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
   
    entities: Optional[List[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    created_at: datetime
   
    analysis_result: Optional[AnalysisResultResponse] = None

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str