"""Admin endpoints - Gestion des utilisateurs et audit logs"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.permissions import require_admin, require_recruiter_or_admin
from app.models.user import User, UserRole
from app.models.auditlog import AuditLog, AuditActionEnum
from app.schemas.user_schema import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    RoleChangeRequest, AuditLogResponse
)
from app.db.session import get_db
from app.core.password import hash_password
from typing import List
from datetime import datetime, timezone


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def log_audit(
    db: Session,
    actor_id: int,
    action: AuditActionEnum,
    resource_type: str,
    resource_id: int,
    description: str = None,
    old_values: dict = None,
    new_values: dict = None
):
    """Enregistrer une action dans l'audit log"""
    audit = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
    )
    db.add(audit)
    db.commit()


@router.get("/users", response_model=List[UserDetailResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister tous les utilisateurs (ADMIN uniquement)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acces refuse")
    
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recuperer les details d'un utilisateur"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acces refuse")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    
    return user


@router.post("/users", response_model=UserDetailResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creer un nouvel utilisateur (ADMIN uniquement)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acces refuse")
    
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email deja utilise")
    
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_audit(
        db=db,
        actor_id=current_user.id,
        action=AuditActionEnum.USER_CREATED,
        resource_type="User",
        resource_id=new_user.id,
        description=f"Utilisateur cree: {user_data.email} ({user_data.role})",
        new_values={"email": user_data.email, "role": user_data.role.value}
    )
    
    return new_user


@router.patch("/users/{user_id}/role", response_model=UserDetailResponse)
async def change_user_role(
    user_id: int,
    role_data: RoleChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Changer le role d'un utilisateur"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acces refuse")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    
    old_role = user.role.value if user.role else None
    user.role = role_data.new_role
    db.commit()
    db.refresh(user)
    
    log_audit(
        db=db,
        actor_id=current_user.id,
        action=AuditActionEnum.USER_ROLE_CHANGED,
        resource_type="User",
        resource_id=user.id,
        description=f"Role change: {user.email} {old_role} -> {role_data.new_role.value}",
        old_values={"role": old_role},
        new_values={"role": role_data.new_role.value}
    )
    
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Supprimer un utilisateur"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acces refuse")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Impossible de vous supprimer")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    
    email = user.email
    db.delete(user)
    db.commit()
    
    log_audit(
        db=db,
        actor_id=current_user.id,
        action=AuditActionEnum.USER_DELETED,
        resource_type="User",
        resource_id=user_id,
        description=f"Utilisateur supprime: {email}"
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recuperer les logs d'audit (ADMIN uniquement)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acces refuse")
    
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs
