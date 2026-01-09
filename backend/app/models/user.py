import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func
from app.db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.RECRUITER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Pas de relation 'offers' définie (relations unidirectionnelles)
