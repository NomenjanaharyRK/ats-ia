from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferUpdate, OfferRead

router = APIRouter(prefix="/offers", tags=["offers"])

@router.post("", response_model=OfferRead)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db)):
    offer = Offer(title=payload.title, description=payload.description, status=payload.status)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer

@router.get("", response_model=list[OfferRead])
def list_offers(db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.deleted == False).order_by(Offer.id.desc()).all()  # noqa: E712

@router.get("/{offer_id}", response_model=OfferRead)
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer

@router.put("/{offer_id}", response_model=OfferRead)
def update_offer(offer_id: int, payload: OfferUpdate, db: Session = Depends(get_db)):
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(offer, k, v)

    db.commit()
    db.refresh(offer)
    return offer

@router.delete("/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.get(Offer, offer_id)
    if not offer or offer.deleted:
        raise HTTPException(status_code=404, detail="Offer not found")
    offer.deleted = True
    db.commit()
    return {"status": "deleted"}
