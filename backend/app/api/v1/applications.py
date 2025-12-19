from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session, joinedload

from app.db.deps import get_db
from app.models.offer import Offer
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.cv_file import CVFile, CVFileStatus
from app.schemas.application import ApplicationRead
from app.core.auth import require_role
from app.models.user import UserRole, User
from app.services.storage import save_cv_file_to_disk
from app.workers.tasks import process_cv_file



router = APIRouter(prefix="/offers", tags=["applications"])


@router.post("/{offer_id}/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application_with_cv(
    offer_id: int,
    full_name: str = Form(...),
    email: str | None = Form(None),
    phone: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    # Vérifier que l’offre existe et appartient bien au user (sauf admin)
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validation simple du fichier
    allowed_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    # 1) créer le candidat
    candidate = Candidate(full_name=full_name, email=email, phone=phone)
    db.add(candidate)
    db.flush()  # obtient candidate.id sans commit

    # 2) créer la candidature
    application = Application(offer_id=offer.id, candidate_id=candidate.id)
    db.add(application)
    db.flush()

    # 3) sauvegarde fichier sur disque
    storage_path, size_bytes, sha256 = save_cv_file_to_disk(file)

    cv_file = CVFile(
        application_id=application.id,
        storage_path=storage_path,
        original_filename=file.filename,
        mime_type=file.content_type,
        size_bytes=size_bytes,
        sha256=sha256,
        status=CVFileStatus.UPLOADED.value,
    )
    db.add(cv_file)
    db.commit()
    db.refresh(application)
    db.refresh(candidate)
    db.refresh(cv_file)

    # 4) lancer la tâche asynchrone
    process_cv_file.delay(cv_file.id)

    return application

@router.get("/{offer_id}/applications", response_model=List[ApplicationRead])
def list_applications_for_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    # vérifier offre + droits
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    apps = (
        db.query(Application)
        .options(joinedload(Application.candidate))
        .filter(Application.offer_id == offer_id)
        .order_by(Application.id.desc())
        .all()
    )
    return apps