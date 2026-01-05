"""Permission decorators pour RBAC (Admin + Recruiter)"""
from fastapi import HTTPException, status, Depends
from app.models.user import User, UserRole
from app.core.auth import get_current_user
from typing import List, Union, Callable
from functools import wraps


def require_role(allowed_roles: Union[UserRole, List[UserRole]]):
    """Decorator pour restreindre l'acces aux routes selon le role"""
    if isinstance(allowed_roles, UserRole):
        allowed_roles = [allowed_roles]
    
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> any:
            current_user: User = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Non authentifie"
                )
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acces refuse. Roles requis: {[r.value for r in allowed_roles]}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin():
    """Shortcut: ADMIN uniquement"""
    return require_role(UserRole.ADMIN)


def require_recruiter_or_admin():
    """Shortcut: RECRUITER ou ADMIN"""
    return require_role([UserRole.RECRUITER, UserRole.ADMIN])
