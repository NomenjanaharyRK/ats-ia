"""Permission management module for role-based access control (RBAC).

This module provides enums and utilities to check permissions
for authenticated users across the ATS-IA platform.
"""

from enum import Enum
from typing import Callable, List
from functools import wraps

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User


class Permission(str, Enum):
    """Enumeration of available permissions in the system."""

    # Offer management permissions
    CREATE_OFFER = "create_offer"
    READ_OFFER = "read_offer"
    UPDATE_OFFER = "update_offer"
    DELETE_OFFER = "delete_offer"
    PUBLISH_OFFER = "publish_offer"

    # Candidate management permissions
    READ_CANDIDATE = "read_candidate"
    EVALUATE_CANDIDATE = "evaluate_candidate"
    SHORTLIST_CANDIDATE = "shortlist_candidate"
    REJECT_CANDIDATE = "reject_candidate"

    # User management permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_TEAMS = "manage_teams"

    # System permissions
    VIEW_ANALYTICS = "view_analytics"
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_SYSTEM = "manage_system"


class Role(str, Enum):
    """Role enumeration for different user types."""

    ADMIN = "admin"
    RECRUITER = "recruiter"
    MANAGER = "manager"
    CANDIDATE = "candidate"


# Role-permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.CREATE_OFFER,
        Permission.READ_OFFER,
        Permission.UPDATE_OFFER,
        Permission.DELETE_OFFER,
        Permission.PUBLISH_OFFER,
        Permission.READ_CANDIDATE,
        Permission.EVALUATE_CANDIDATE,
        Permission.SHORTLIST_CANDIDATE,
        Permission.REJECT_CANDIDATE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.MANAGE_TEAMS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_AUDIT_LOG,
        Permission.MANAGE_SYSTEM,
    ],
    Role.RECRUITER: [
        Permission.CREATE_OFFER,
        Permission.READ_OFFER,
        Permission.UPDATE_OFFER,
        Permission.PUBLISH_OFFER,
        Permission.READ_CANDIDATE,
        Permission.EVALUATE_CANDIDATE,
        Permission.SHORTLIST_CANDIDATE,
        Permission.REJECT_CANDIDATE,
        Permission.VIEW_ANALYTICS,
    ],
    Role.MANAGER: [
        Permission.READ_OFFER,
        Permission.READ_CANDIDATE,
        Permission.EVALUATE_CANDIDATE,
        Permission.SHORTLIST_CANDIDATE,
        Permission.VIEW_ANALYTICS,
    ],
    Role.CANDIDATE: [
        Permission.READ_OFFER,
    ],
}


def get_user_permissions(user: User) -> List[Permission]:
    """Get all permissions for a user based on their role."""
    if not user or not hasattr(user, "role"):
        return []

    return ROLE_PERMISSIONS.get(user.role, [])


def has_permission(user: User, required_permission: Permission) -> bool:
    """Check if user has a specific permission."""
    if not user:
        return False

    user_permissions = get_user_permissions(user)
    return required_permission in user_permissions


def require_permission(permission: Permission):
    """Decorator to check if user has required permission.

    Usage:
        @router.get("/offers")
        @require_permission(Permission.READ_OFFER)
        def get_offers(current_user: User = Depends(get_current_user)):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Required: {permission.value}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_offer_access(
    user: User,
    offer_id: int,
    permission: Permission,
    db: Session,
) -> bool:
    """Check if user can access a specific offer."""
    from app.models.offer import Offer

    # Admins can always access
    if user.role == Role.ADMIN:
        return True

    # Check if user has the base permission
    if not has_permission(user, permission):
        return False

    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        return False

    # Recruiters and managers can only access offers from their team
    if user.role in [Role.RECRUITER, Role.MANAGER]:
        if not hasattr(user, "team_id"):
            return False
        return offer.team_id == user.team_id

    return True


def check_candidate_access(
    user: User,
    candidate_id: int,
    permission: Permission,
    db: Session,
) -> bool:
    """Check if user can access a specific candidate."""
    # Admins can always access
    if user.role == Role.ADMIN:
        return True

    # Check if user has the base permission
    if not has_permission(user, permission):
        return False

    # Candidates can only view their own profile
    if user.role == Role.CANDIDATE:
        return user.id == candidate_id

    return True
