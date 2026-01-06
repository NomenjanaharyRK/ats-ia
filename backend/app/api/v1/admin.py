"""Administration endpoints for user, role, and team management.

This module provides REST API endpoints for administrative operations
such as managing users, roles, teams, and viewing audit logs.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.v1.auth import get_current_user
    Permission, Role, require_permission, has_permission
)
from app.models.user import User
from app.schemas.user_schema import (
    UserCreate, UserResponse, UserUpdate, UserListResponse,
    UserDetailResponse, RoleResponse, TeamResponse, TeamCreate,
    TeamUpdate, TeamDetailResponse, AuditLogResponse
)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_user)]
)


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List all users",
    description="Get paginated list of all users. Requires MANAGE_USERS permission."
)
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """List all users with optional filtering."""
    if not has_permission(current_user, Permission.MANAGE_USERS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to manage users"
        )
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return UserListResponse(
        users=[UserResponse.from_orm(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get(
    "/users/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user details"
)
def get_user_details(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed information about a specific user."""
    if not has_permission(current_user, Permission.MANAGE_USERS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserDetailResponse.from_orm(user)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user information"
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user information. Admins can update any user, others can only update themselves."""
    # Check if user can edit this user
    if current_user.id != user_id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own user or be an admin"
        )
    
    if not has_permission(current_user, Permission.MANAGE_USERS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate user"
)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deactivate a user (soft delete)."""
    if not has_permission(current_user, Permission.MANAGE_USERS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()


# ============================================================================
# TEAM MANAGEMENT ENDPOINTS
# ============================================================================

@router.get(
    "/teams",
    response_model=List[TeamResponse],
    summary="List all teams"
)
def list_teams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all teams."""
    if not has_permission(current_user, Permission.MANAGE_TEAMS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # For now, return empty list - teams table doesn't exist yet
    return []


@router.post(
    "/teams",
    response_model=TeamResponse,
    summary="Create new team"
)
def create_team(
    team_create: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new team."""
    if not has_permission(current_user, Permission.MANAGE_TEAMS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Team creation will be implemented when Team model is added
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Team management coming soon"
    )


# ============================================================================
# ROLE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get(
    "/roles",
    response_model=List[RoleResponse],
    summary="List all roles"
)
def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all available roles."""
    if not has_permission(current_user, Permission.MANAGE_ROLES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Return predefined roles
    roles = [
        RoleResponse(id=1, name="admin", permissions=[]),
        RoleResponse(id=2, name="recruiter", permissions=[]),
        RoleResponse(id=3, name="manager", permissions=[]),
        RoleResponse(id=4, name="candidate", permissions=[]),
    ]
    return roles


# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    summary="View audit logs"
)
def get_audit_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get audit logs for system actions. Requires VIEW_AUDIT_LOG permission."""
    if not has_permission(current_user, Permission.VIEW_AUDIT_LOG):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view audit logs"
        )
    
    # Audit logging implementation
    # This will query AuditLog model when implemented
    return []


# ============================================================================
# SYSTEM HEALTH ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    summary="System health status"
)
def get_system_health(
    current_user: User = Depends(get_current_user),
):
    """Get system health information. Admin only."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view system health"
        )
    
    return {
        "status": "ok",
        "message": "System is operational"
    }
