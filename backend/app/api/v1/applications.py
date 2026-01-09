# backend/app/api/v1/applications.py
from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Query,
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

router = APIRouter(prefix="/applications", tags=["applications"])


# ========================================
# ✅ NOUVEAU: Endpoint pour TOUTES les candidatures
# ========================================
@router.get(
    "",
    response_model=List[ApplicationRead],
)
def get_all_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_job_offer: bool = Query(False),
    include_cv_file: bool = Query(False),
    include_scoring: bool = Query(False),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """
    Récupère toutes les candidatures (avec relations optionnelles).
    
    Params:
    - include_job_offer: Inclure les infos de l'offre d'emploi
    - include_cv_file: Inclure les infos du fichier CV
    - include_scoring: Inclure le scoring/parsed_cv détaillé
    - status: Filtrer par statut (UPLOADED, PROCESSING, EXTRACTED, ERROR)
    """
    query = db.query(Application)
    
    # Filtrer par owner si non-admin
    if current_user.role != UserRole.ADMIN:
        query = query.join(Offer).filter(Offer.owner_id == current_user.id)
    
    # Filtrer par statut si fourni
    if status_filter:
        query = query.join(CVFile, Application.id == CVFile.application_id).filter(
            CVFile.status == status_filter
        )
    
    # Options de chargement eager (évite N+1 queries)
    options = [joinedload(Application.candidate)]
    
    if include_job_offer:
        options.append(joinedload(Application.offer))
    
    if include_cv_file:
        # CVFile n'est pas dans les relations mais on peut le joindre via cv_text
        pass  # On va le gérer dans le schéma
    
    if include_scoring:
        options.append(joinedload(Application.parsed_cv))
    
    query = query.options(*options)
    
    # Pagination
    applications = query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
    
    return applications


# ========================================
# ✅ NOUVEAU: Endpoint pour récupérer UNE candidature par ID
# ========================================
@router.get(
    "/{application_id}",
    response_model=ApplicationRead,
)
def get_application_by_id(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """Récupère une candidature spécifique par ID."""
    application = (
        db.query(Application)
        .options(
            joinedload(Application.candidate),
            joinedload(Application.offer),
            joinedload(Application.cv_text),
            joinedload(Application.parsed_cv),
        )
        .filter(Application.id == application_id)
        .first()
    )
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Vérifier les permissions
    if current_user.role != UserRole.ADMIN:
        if application.offer.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    
    return application


# ========================================
# Endpoints existants (pour compatibilité)
# ========================================
@router.post(
    "/offers/{offer_id}",
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
    """Crée une candidature pour une offre donnée, avec upload de CV."""
    # 1) Vérifier que l'offre existe
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")

    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2) Validation fichier
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
    db.flush()

    # 4) Créer la candidature
    application = Application(offer_id=offer.id, candidate_id=candidate.id)
    db.add(application)
    db.flush()

    # 5) Créer l'entrée CVText
    cv_text = CVText(
        application_id=application.id,
        status="PENDING",
    )
    db.add(cv_text)

    # 6) Sauvegarder le fichier
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

    # 7) Lancer tâche asynchrone
    process_cv_file.delay(cv_file.id)

    return application


@router.get(
    "/offers/{offer_id}",
    response_model=List[ApplicationRead],
)
def list_applications_for_offer(
    offer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    """Liste les candidatures pour une offre donnée."""
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")

    if current_user.role != UserRole.ADMIN and offer.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    apps = (
        db.query(Application)
        .filter(Application.offer_id == offer_id)
        .options(
            joinedload(Application.candidate),
            joinedload(Application.cv_text),
            joinedload(Application.parsed_cv),
        )
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return apps
