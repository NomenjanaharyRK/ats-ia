"""Pydantic schemas for user management.

Defines request/response schemas for user-related operations.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class RoleType(str, Enum):
    """User role types."""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    MANAGER = "manager"
    CANDIDATE = "candidate"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: RoleType = RoleType.CANDIDATE
    is_active: bool = True

    class Config:
        from_attributes = True
        use_enum_values = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    team_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    role: Optional[RoleType] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class UserChangePassword(BaseModel):
    """Schema for changing user password."""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)


class UserPasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime
    team_id: Optional[int] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class UserDetailResponse(UserResponse):
    """Detailed user response with additional information."""
    last_login: Optional[datetime] = None
    login_count: int = 0
    is_email_verified: bool = False

    class Config:
        from_attributes = True
        use_enum_values = True


class UserListResponse(BaseModel):
    """Schema for listing multiple users with pagination."""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PermissionResponse(BaseModel):
    """Schema for permission response."""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Schema for role response."""
    id: int
    name: RoleType
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True
        use_enum_values = True


class RoleCreateUpdate(BaseModel):
    """Schema for creating/updating roles."""
    name: RoleType
    description: Optional[str] = None
    permission_ids: List[int] = []

    class Config:
        use_enum_values = True


class TeamResponse(BaseModel):
    """Schema for team response."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    """Schema for creating a team."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class TeamDetailResponse(TeamResponse):
    """Detailed team response with members."""
    members: List[UserResponse] = []

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """Schema for audit log entry."""
    id: int
    user_id: int
    action: str
    resource_type: str
    resource_id: int
    details: Optional[dict] = None
    timestamp: datetime

    class Config:
        from_attributes = True
