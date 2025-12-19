from pydantic import BaseModel
from typing import Optional

class CandidateCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class CandidateRead(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True
