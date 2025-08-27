import datetime
from typing import Optional

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy import func
from sqlalchemy.future import select
from sqlmodel import Session, select

from data.user import User, UserRole


def user_count(session: Session) -> int:
    query = select(func.count(User.id))
    result = session.exec(query)
    return result.all()[0]


def create_user(
    session: Session,
    name: Optional[str],
    email: Optional[str],
    password: Optional[str],
    role: UserRole = UserRole.USER,
) -> User:
    if not password:
        raise Exception("password is required")
    if not email:
        raise Exception("email is required")
    if not name:
        raise Exception("name is required")

    user = User()
    user.email = email
    user.name = name
    user.role = role
    user.hash_password = crypto.hash(password, rounds=172_434)

    session.add(user)
    session.commit()
    return user


def update_user(
    session: Session,
    user_id: int,
    name: str,
    email: str,
    role: str,
    password: str = None,
):
    user = session.get(User, user_id)
    if not user:
        return None

    user.name = name
    user.email = email
    user.role = UserRole(role)

    if password:  # Only update password if provided
        user.hash_password = crypto.hash(password, rounds=172_434)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> bool:
    """
    Delete a user by ID

    Args:
        session: Database session
        user_id: ID of the user to delete

    Returns:
        bool: True if user was deleted successfully, False otherwise
    """
    try:
        user = session.get(User, user_id)
        if not user:
            return False

        # You might want to handle related records here
        # For example, if you have foreign key constraints,
        # you might need to delete or update related records first

        session.delete(user)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting user {user_id}: {e}")
        return False


def login_user(session: Session, email: str, password: str) -> Optional[User]:
    query = select(User).filter(User.email == email)
    results = session.exec(query)

    user = results.one_or_none()
    if not user:
        return user

    try:
        if not crypto.verify(password, user.hash_password):
            return None
    except ValueError:
        return None

    # update last_login
    user.last_login = datetime.datetime.now()
    session.add(user)
    session.commit()

    return user


def create_first_superadmin(session: Session, name: str, email: str, password: str):
    """Create the first superadmin user - only if no users exist"""
    if user_count(session) > 0:
        print("Cannot create superadmin when users already exist")
    else:
        create_user(session, name, email, password, UserRole.SUPERADMIN)


def get_user_by_id(session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    query = select(User).filter(User.email == email)
    result = session.exec(query)

    return result.one_or_none()


def update_user_role(
    session: Session, user_id: int, new_role: UserRole, current_user: User
) -> Optional[User]:
    """Update user role - only admins can change roles"""
    if not current_user.is_admin():
        raise Exception("Only administrators can change user roles")

    # Prevent non-superadmins from creating superadmins
    if new_role == UserRole.SUPERADMIN and not current_user.is_superadmin():
        raise Exception("Only superadmins can create other superadmins")

    # Prevent users from changing their own role
    if user_id == current_user.id:
        raise Exception("Cannot change your own role")

    user = session.get(User, user_id)
    if not user:
        return None

    user.role = new_role
    session.add(user)
    session.commit()
    return user


def get_users_by_role(session: Session, role: UserRole) -> list[User]:
    """Get all users with a specific role"""
    query = select(User).filter(User.role == role)
    results = session.exec(query)
    return results.all()
