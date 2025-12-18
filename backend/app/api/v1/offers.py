from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.offer import Offer
from app.models.user import UserRole, User
from app.schemas.offer import OfferCreate, OfferUpdate, OfferRead
from app.core.auth import require_role


router = APIRouter(prefix="/offers", tags=["offers"])


def _get_offer_or_404(db: Session, offer_id: int) -> Offer:
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


def _ensure_can_access_offer(current_user: User, offer: Offer) -> None:
    # ADMIN: accès total
    if current_user.role == UserRole.ADMIN:
        return
    # RECRUITER: seulement ses offres
    if offer.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("", response_model=OfferRead)
def create_offer(
    payload: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    offer = Offer(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        owner_id=current_user.id,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.get("", response_model=list[OfferRead])
def list_offers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    q = db.query(Offer).filter(Offer.deleted == False)  # noqa: E712

    if current_user.role != UserRole.ADMIN:
        q = q.filter(Offer.owner_id == current_user.id)

    return q.order_by(Offer.id.desc()).all()


@router.get("/{offer_id}", response_model=OfferRead)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    offer = _get_offer_or_404(db, offer_id)
    _ensure_can_access_offer(current_user, offer)
    return offer


@router.put("/{offer_id}", response_model=OfferRead)
def update_offer(
    offer_id: int,
    payload: OfferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    offer = _get_offer_or_404(db, offer_id)
    _ensure_can_access_offer(current_user, offer)

    data = payload.model_dump(exclude_unset=True)

    # Sécurité: un recruteur ne peut pas "voler" une offre en changeant owner_id
    if "owner_id" in data:
        data.pop("owner_id")

    for k, v in data.items():
        setattr(offer, k, v)

    db.commit()
    db.refresh(offer)
    return offer


@router.delete("/{offer_id}")
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER)),
):
    offer = _get_offer_or_404(db, offer_id)
    _ensure_can_access_offer(current_user, offer)

    offer.deleted = True
    db.commit()
    return {"status": "deleted"}
