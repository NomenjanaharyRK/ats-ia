"""Modèle pour stocker les CV parsés avec informations structurées"""
from sqlalchemy import Column, Integer, String, JSON, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class ParsedCV(Base):
    """Stockage des informations structurées extraites des CV"""
    __tablename__ = "parsed_cvs"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True, nullable=False, index=True)
    
    # Informations de contact
    full_name = Column(String(255), index=True)
    email = Column(String(255))
    phone = Column(String(50))
    
    # Compétences (JSON array) - Ex: ["Python", "FastAPI", "PostgreSQL"]
    skills = Column(JSON, nullable=False, default=list)
    
    # Expérience
    experience_years = Column(Integer)
    
    # Éducation (JSON array) - Ex: ["Master Informatique", "Licence Mathématiques"]
    education = Column(JSON, nullable=False, default=list)
    
    # Langues (JSON array) - Ex: ["Français", "Anglais"]
    languages = Column(JSON, nullable=False, default=list)
    
    # Scoring
    matching_score = Column(Float, default=0.0, index=True)
    skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    language_score = Column(Float, default=0.0)
    
    # Détails du scoring (JSON object)
    scoring_details = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    application = relationship("Application", back_populates="parsed_cv")
