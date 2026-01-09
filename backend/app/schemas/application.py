# backend/app/schemas/application.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, computed_field
from app.schemas.candidate import CandidateRead
from app.schemas.offer import OfferRead
from app.schemas.parsed_cv import ParsedCVResponse  # ✅ CORRECTION: ParsedCVResponse au lieu de ParsedCVRead


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    offer_id: int
    candidate_id: int
    created_at: datetime
    
    # Relations (toujours présent)
    candidate: CandidateRead
    
    # Relations optionnelles
    offer: Optional[OfferRead] = None
    parsed_cv: Optional[ParsedCVResponse] = None  # ✅ CORRECTION: ParsedCVResponse
    
    # Computed fields pour faciliter l'affichage frontend
    @computed_field
    @property
    def fullname(self) -> str:
        return self.candidate.full_name
    
    @computed_field
    @property
    def email(self) -> str:
        return self.candidate.email or ""
    
    @computed_field
    @property
    def phone(self) -> str:
        return self.candidate.phone or ""
    
    @computed_field
    @property
    def status(self) -> str:
        """
        Retourne le statut du traitement CV.
        Basé sur parsed_cv si disponible.
        """
        if self.parsed_cv:
            # Si on a un scoring complet
            if self.parsed_cv.matching_score is not None and self.parsed_cv.matching_score > 0:
                return 'SCORED'
            # Si on a des données extraites mais pas encore de score
            elif self.parsed_cv.full_name or self.parsed_cv.skills:
                return 'EXTRACTED'
        
        # Par défaut
        return 'UPLOADING'
    
    @computed_field
    @property
    def scoring(self) -> Optional[dict]:
        """
        Retourne les données de scoring si disponibles.
        Format compatible avec le frontend.
        """
        if self.parsed_cv and self.parsed_cv.matching_score is not None:
            return {
                "id": self.parsed_cv.id,
                "overall_score": round(self.parsed_cv.matching_score, 2),
                "details": {
                    "education_score": round(self.parsed_cv.education_score or 0, 2),
                    "experience_score": round(self.parsed_cv.experience_score or 0, 2),
                    "skills_score": round(self.parsed_cv.skills_score or 0, 2),
                    "language_score": round(self.parsed_cv.language_score or 0, 2),
                    "matching_skills": self.parsed_cv.skills or [],
                    "years_experience": self.parsed_cv.experience_years,
                    "education": self.parsed_cv.education or [],
                    "languages": self.parsed_cv.languages or [],
                },
                "created_at": self.parsed_cv.created_at.isoformat() if self.parsed_cv.created_at else None,
            }
        return None
