from pydantic import BaseModel
from typing import Optional

class OfferCreate(BaseModel):
    title: str
    description: str
    status: str = "DRAFT"

class OfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    deleted: Optional[bool] = None

class OfferRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    deleted: bool

    class Config:
        from_attributes = True
