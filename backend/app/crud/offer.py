from typing import List, Optional, Dict, Any, Union  # ✅ IMPORTS AJOUTÉS
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferUpdate


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> List[Offer]:
    """Récupère plusieurs offres"""
    query = db.query(Offer).filter(Offer.deleted == False)
    
    if status:
        query = query.filter(Offer.status == status)
    
    return query.offset(skip).limit(limit).all()


def get(db: Session, id: int) -> Optional[Offer]:
    """Récupère une offre par ID"""
    return db.query(Offer).filter(Offer.id == id, Offer.deleted == False).first()


def create(
    db: Session,
    *,
    obj_in: OfferCreate,
    owner_id: Optional[int] = None,
) -> Offer:
    """Crée une nouvelle offre"""
    dict_data = obj_in.model_dump(exclude_unset=True)
    if owner_id is not None:
        dict_data["owner_id"] = owner_id
    
    db_obj = Offer(**dict_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session,
    *,
    db_obj: Offer,
    obj_in: Union[OfferUpdate, Dict[str, Any]],  # ✅ CORRIGÉ
) -> Offer:
    """Met à jour une offre"""
    update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
