from pydantic import BaseModel
from typing import Optional
from app.schemas.candidate import CandidateRead


class ApplicationRead(BaseModel):
    id: int
    offer_id: int
    candidate: CandidateRead

    class Config:
        from_attributes = True
