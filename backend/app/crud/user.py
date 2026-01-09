from sqlalchemy.orm import Session
from app.models.user import User


def get(db: Session, id: int) -> User:
    """Récupère un utilisateur par ID"""
    return db.query(User).filter(User.id == id).first()
