from pydantic import BaseModel


class ApplicationScore(BaseModel):
    application_id: int
    candidate_full_name: str
    score: int
