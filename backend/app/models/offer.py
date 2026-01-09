# backend/app/models/offer.py
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="DRAFT")
    deleted = Column(Boolean, nullable=False, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # ✅ NOUVEAUX CHAMPS pour le scoring
    required_skills = Column(JSON, nullable=True, default=list)
    nice_to_have_skills = Column(JSON, nullable=True, default=list)
    min_experience_years = Column(Integer, nullable=True, default=0)
    required_education = Column(JSON, nullable=True, default=list)
    required_languages = Column(JSON, nullable=True, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
