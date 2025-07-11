"""
FastAPI dependencies for database sessions, authentication, etc.
"""

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from config import Settings
from data.user import User
from database import SessionLocal
from infrastructure.cookie_auth import get_user_id_via_auth_cookie
from services.user_service import get_user_by_id


@lru_cache
def get_settings():
    return Settings()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
    user_id: Optional[int] = None,
) -> Optional[User]:
    user_id = get_user_id_via_auth_cookie(request)

    if not user_id:
        return None

    user = get_user_by_id(session, user_id)
    return user


def get_current_user_required(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current authenticated user, raising an exception if not authenticated.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user
