from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.db.base import Base


class AuditActionEnum(str, PyEnum):
    """Actions tracées dans les logs d'audit"""
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    OFFER_CREATED = "OFFER_CREATED"
    OFFER_UPDATED = "OFFER_UPDATED"
    OFFER_DELETED = "OFFER_DELETED"
    APPLICATION_SUBMITTED = "APPLICATION_SUBMITTED"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"


class AuditLog(Base):
    """Table de journalisation des actions sensibles"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=False, index=True)  # user_id qui a fait l'action
    action = Column(Enum(AuditActionEnum), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)  # "User", "Offer", "Application"
    resource_id = Column(Integer, nullable=False, index=True)  # ID de la ressource affectée
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)  # Ancien state si mise à jour
    new_values = Column(JSON, nullable=True)  # Nouveau state
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
