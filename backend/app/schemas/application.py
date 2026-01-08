from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.candidate import CandidateRead


class CVTextRead(BaseModel):
    """Schema pour CVText avec le status"""
    id: int
    status: str
    extracted_text: Optional[str] = None
    quality_score: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationRead(BaseModel):
    """Schema pour Application"""
    id: int
    offer_id: int
    candidate: CandidateRead
    cv_text: Optional[CVTextRead] = None  # ✅ Inclut le status via CVText
    created_at: datetime

    class Config:
        from_attributes = True
