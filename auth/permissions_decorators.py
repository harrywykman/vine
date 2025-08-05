"""
Permission decorators and dependencies for role-based access control.
"""

from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from data.user import User, UserRole
from dependencies import get_session
from infrastructure import cookie_auth
from services.user_service import get_user_by_id


def get_current_user_from_request(request: Request, session: Session) -> Optional[User]:
    """Get current user from request using your existing cookie auth"""
    user_id = cookie_auth.get_user_id_via_auth_cookie(request)
    if not user_id:
        return None
    return get_user_by_id(session, user_id)


def require_permission(required_role: UserRole, redirect_url: str = "/login"):
    """
    Decorator to require specific permission level for routes.
    Can be used with both API endpoints and template routes.

    Args:
        required_role: Minimum role required to access the route
        redirect_url: URL to redirect to if user is not authenticated (for template routes)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get current_user from kwargs (dependency injection)
            current_user = kwargs.get("current_user")
            request = kwargs.get("request")
            session = kwargs.get("session")

            # If we have request and session but no current_user, try to get it from cookie
            if not current_user and request and session:
                current_user = get_current_user_from_request(request, session)

            if not current_user:
                # If template route, redirect to login
                if request and hasattr(request, "url"):
                    return RedirectResponse(url=redirect_url, status_code=302)
                else:
                    # If API route, return 401
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

            if not current_user.has_permission(required_role):
                if request and hasattr(request, "url"):
                    # For template routes, redirect to unauthorized page
                    return RedirectResponse(url="/unauthorized", status_code=302)
                else:
                    # For API routes, return 403
                    raise HTTPException(
                        status_code=403,
                        detail=f"Insufficient permissions. Required: {required_role.value}",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Convenience decorators for common roles
def require_superadmin(redirect_url: str = "/account/login"):
    """Decorator that requires superadmin role"""
    return require_permission(UserRole.SUPERADMIN, redirect_url)


def require_admin(redirect_url: str = "/account/login"):
    """Decorator that requires admin role or higher"""
    return require_permission(UserRole.ADMIN, redirect_url)


def require_operator(redirect_url: str = "/account/login"):
    """Decorator that requires operator role or higher"""
    return require_permission(UserRole.OPERATOR, redirect_url)


# FastAPI dependencies for permission checking
def require_role(required_role: UserRole):
    """
    FastAPI dependency for role-based access control using cookie auth.
    """

    def check_permission(request: Request, session: Session = Depends(get_session)):
        current_user = get_current_user_from_request(request, session)

        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_role.value}",
            )
        return current_user

    return check_permission


# Specific role dependencies for convenience
def require_superadmin_user():
    """FastAPI dependency that returns superadmin user"""
    return require_role(UserRole.SUPERADMIN)


def require_admin_user():
    """FastAPI dependency that returns admin user or higher"""
    return require_role(UserRole.ADMIN)


def require_operator_user():
    """FastAPI dependency that returns operator user or higher"""
    return require_role(UserRole.OPERATOR)


def require_authenticated_user():
    """FastAPI dependency that returns any authenticated user"""
    return require_role(UserRole.USER)
