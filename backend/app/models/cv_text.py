from sqlalchemy import Column, Integer, ForeignKey, Text, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base 


class CVText(Base):
    __tablename__ = "cv_texts"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    status = Column(String(20), nullable=False, default="PENDING")  # PENDING|SUCCESS|FAILED
    extracted_text = Column(Text, nullable=True)
    language = Column(String(10), nullable=True)
    quality_score = Column(Integer, nullable=True)  # 0-100, optionnel
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    application = relationship("Application", back_populates="cv_text", uselist=False)
