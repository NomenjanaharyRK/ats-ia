from pydantic import BaseModel
from typing import Optional


class CVTextRead(BaseModel):
    application_id: int
    status: str
    extracted_text: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
