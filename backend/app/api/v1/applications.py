from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
)
from sqlalchemy.orm import Session, joinedload

from app.db.deps import get_db
from app.models.offer import Offer
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.cv_text import CVText
from app.models.cv_file import CVFile, CVFileStatus
from app.schemas.application import ApplicationRead
from app.core.auth import require_role
from app.models.user import UserRole, User
from app.services.storage import save_cv_file_to_disk
from app.workers.tasks import process_cv_file


router = APIRouter(prefix="/offers", tags=["applications"])


@router.post(
    "/{offer_id}/applications",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_application_with_cv(
    offer_id: int,
    full_name: str = Form(...),
    email: str | None = Form(None),
    phone: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """
    Crée une candidature pour une offre donnée, avec upload de CV.

    Étapes :
    1. Vérifier l'offre + permissions (ADMIN ou owner).
    2. Valider le type de fichier.
    3. Créer le Candidate.
    4. Créer l'Application.
    5. Créer l'enregistrement CVText en PENDING (texte à extraire plus tard).
    6. Sauvegarder le fichier sur disque et créer CVFile.
    7. Commit de la transaction.
    8. Déclenchement de la tâche Celery process_cv_file.
    """

    # 1) Vérifier que l’offre existe et appartient bien au user (sauf admin)
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2) Validation simple du fichier (whitelist de MIME types)
    allowed_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # 3) Créer le candidat
    candidate = Candidate(full_name=full_name, email=email, phone=phone)
    db.add(candidate)
    db.flush()  # récupère candidate.id sans commit

    # 4) Créer la candidature
    application = Application(offer_id=offer.id, candidate_id=candidate.id)
    db.add(application)
    db.flush()  # récupère application.id

    # 5) Créer l'entrée CVText liée à cette candidature
    cv_text = CVText(
        application_id=application.id,
        status="PENDING",
    )
    db.add(cv_text)

    # 6) Sauvegarder le fichier sur disque et créer CVFile
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

    # Commit unique de toutes les écritures ci‑dessus
    db.commit()

    # Rafraîchir les objets retournés (pour avoir les IDs / champs calculés)
    db.refresh(application)
    db.refresh(candidate)
    db.refresh(cv_file)

    # 7) Lancer la tâche asynchrone d'extraction/traitement du CV
    process_cv_file.delay(cv_file.id)

    # Le schéma ApplicationRead s'occupe de la sérialisation
    return application


@router.get(
    "/{offer_id}/applications",
    response_model=List[ApplicationRead],
)
def list_applications_for_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """
    Liste toutes les candidatures d'une offre donnée, pour l'owner ou un admin.
    """

    # Vérifier offre + droits
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Charger les candidatures + candidat associé (joinedload pour éviter N+1)
    apps = (
        db.query(Application)
        .options(joinedload(Application.candidate))
        .filter(Application.offer_id == offer_id)
        .order_by(Application.id.desc())
        .all()
    )

    return apps
