from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Pas de relation 'applications' définie ici (relations unidirectionnelles)
