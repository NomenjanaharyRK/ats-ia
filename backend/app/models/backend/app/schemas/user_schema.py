from pydantic import BaseModel, EmailStr
from enum import Enum as PyEnum
from datetime import datetime
from typing import Optional


class UserRoleEnum(str, PyEnum):
    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRoleEnum = UserRoleEnum.RECRUITER


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[UserRoleEnum] = None


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Response avancée (pour Admin) avec plus de champs"""
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class RoleChangeRequest(BaseModel):
    new_role: UserRoleEnum


class AuditLogResponse(BaseModel):
    id: int
    actor_id: int
    action: str
    resource_type: str
    resource_id: int
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
