from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app import crud
from app.schemas.offer import OfferCreate, OfferUpdate, OfferRead
from app.models.offer import Offer

router = APIRouter()


@router.get("/", response_model=List[OfferRead])
def read_offers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user = Depends(get_current_active_user),
):
    """Récupère toutes les offres"""
    offers = crud.offer.get_multi(db, skip=skip, limit=limit, status=status)
    return offers


@router.post("/", response_model=OfferRead)
def create_offer(
    *,
    db: Session = Depends(get_db),
    offer_in: OfferCreate,
    current_user = Depends(get_current_active_user),
):
    """Crée une nouvelle offre"""
    offer = crud.offer.create(db=db, obj_in=offer_in, owner_id=current_user.id)
    return offer


@router.get("/{id}", response_model=OfferRead)
def read_offer(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user),
):
    """Récupère une offre par ID"""
    offer = crud.offer.get(db=db, id=id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return offer


@router.patch("/{id}", response_model=OfferRead)
def update_offer(
    *,
    db: Session = Depends(get_db),
    id: int,
    offer_in: OfferUpdate,
    current_user = Depends(get_current_active_user),
):
    """Met à jour une offre"""
    offer = crud.offer.get(db=db, id=id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    offer = crud.offer.update(db=db, db_obj=offer, obj_in=offer_in)
    return offer


@router.delete("/{id}", response_model=OfferRead)
def delete_offer(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user),
):
    """Archive une offre"""
    offer = crud.offer.get(db=db, id=id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    offer = crud.offer.update(db=db, db_obj=offer, obj_in=OfferUpdate(deleted=True))
    return offer
