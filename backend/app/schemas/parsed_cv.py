"""Schémas Pydantic pour les CV parsés"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ParsedCVBase(BaseModel):
    """Schéma de base pour un CV parsé"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    education: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class ParsedCVCreate(ParsedCVBase):
    """Schéma pour créer un CV parsé"""
    application_id: int
    matching_score: float = 0.0
    skills_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    language_score: float = 0.0
    scoring_details: Optional[Dict] = None


class ParsedCVUpdate(BaseModel):
    """Schéma pour mettre à jour un CV parsé"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    matching_score: Optional[float] = None
    skills_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    language_score: Optional[float] = None
    scoring_details: Optional[Dict] = None


class ParsedCVInDB(ParsedCVBase):
    """Schéma pour un CV parsé en base de données"""
    id: int
    application_id: int
    matching_score: float
    skills_score: float
    experience_score: float
    education_score: float
    language_score: float
    scoring_details: Optional[Dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParsedCVResponse(ParsedCVInDB):
    """Schéma de réponse API pour un CV parsé"""
    pass
