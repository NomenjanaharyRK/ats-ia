from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.deps import get_db
from app.models.application import Application
from app.models.cv_text import CVText
from app.models.user import User, UserRole
from app.core.auth import require_role
from app.schemas.scoring import ApplicationScore
from app.services.scoring import keyword_overlap_score

router = APIRouter(prefix="/applications", tags=["scoring"])

@router.get("/{application_id}/scoring", response_model=Optional[ApplicationScore])
def get_application_scoring(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """
    Retourne le scoring détaillé d'une candidature spécifique.
    """
    
    # Charger l'application + candidate + cv_text
    app = (
        db.query(Application)
        .options(
            joinedload(Application.candidate),
            joinedload(Application.cv_text),
            joinedload(Application.offer),
        )
        .filter(Application.id == application_id)
        .first()
    )
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Vérifier les permissions
    if current_user.role != UserRole.ADMIN and app.offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    cv_text: CVText | None = app.cv_text
    
    # Calculer le score
    if not cv_text or not cv_text.extracted_text or cv_text.status != "SUCCESS":
        score = 0
    else:
        score = keyword_overlap_score(
            job_text=app.offer.description or "",
            cv_text=cv_text.extracted_text or "",
        )
    
    return ApplicationScore(
        application_id=app.id,
        candidate_full_name=app.candidate.full_name,
        score=score,
    )
