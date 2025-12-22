from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.deps import get_db
from app.models.offer import Offer
from app.models.application import Application
from app.models.cv_text import CVText
from app.models.user import User, UserRole
from app.core.auth import require_role
from app.schemas.scoring import ApplicationScore
from app.services.scoring import keyword_overlap_score

router = APIRouter(prefix="/offers", tags=["scoring"])


@router.get("/{offer_id}/applications/scoring", response_model=List[ApplicationScore])
def score_applications_for_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """
    Retourne les candidatures d'une offre avec un score texte (v1) trié décroissant.
    Le score est basé sur le chevauchement de mots entre la description d'offre
    et le texte extrait du CV (cv_texts.extracted_text).
    """

    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Charger applications + candidate + cv_text (LEFT OUTER JOIN sur cv_texts)
    applications = (
        db.query(Application)
        .options(
            joinedload(Application.candidate),
            joinedload(Application.cv_text),
        )
        .filter(Application.offer_id == offer_id)
        .all()
    )

    scored: List[ApplicationScore] = []

    for app_obj in applications:
        cv_text: CVText | None = app_obj.cv_text

        if not cv_text or not cv_text.extracted_text or cv_text.status != "SUCCESS":
            score = 0
        else:
            score = keyword_overlap_score(
                job_text=offer.description or "",
                cv_text=cv_text.extracted_text or "",
            )

        scored.append(
            ApplicationScore(
                application_id=app_obj.id,
                candidate_full_name=app_obj.candidate.full_name,
                score=score,
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored
