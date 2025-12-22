from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.application import Application
from app.models.cv_text import CVText
from app.models.user import User, UserRole
from app.core.auth import require_role
from app.schemas.cv_text import CVTextRead

router = APIRouter(prefix="/applications", tags=["cv-text"])


@router.get("/{application_id}/cv-text", response_model=CVTextRead)
def get_cv_text_for_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """
    Retourne le statut et le texte extrait du CV pour une application donnée.
    """
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if (
        current_user.role != UserRole.ADMIN
        and application.offer.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    cv_text = (
        db.query(CVText)
        .filter(CVText.application_id == application_id)
        .one_or_none()
    )
    if not cv_text:
        raise HTTPException(status_code=404, detail="CV text not found")

    return cv_text
