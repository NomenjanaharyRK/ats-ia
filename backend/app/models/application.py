from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ Relations unidirectionnelles (sans back_populates pour éviter erreurs)
    offer = relationship("Offer")
    candidate = relationship("Candidate")
    
    # Relations bidirectionnelles (avec back_populates)
    cv_text = relationship(
        "CVText",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )

    parsed_cv = relationship(
        "ParsedCV",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )
