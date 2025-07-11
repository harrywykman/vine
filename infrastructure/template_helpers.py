"""
Template helper functions for permission checking in Chameleon templates
"""

from typing import Optional

from data.user import User, UserRole


def has_permission(user: Optional[User], required_role: UserRole) -> bool:
    """Template helper to check if user has required permission"""
    if not user:
        return False
    return user.has_permission(required_role)


def is_admin(user: Optional[User]) -> bool:
    """Template helper to check if user is admin"""
    if not user:
        return False
    return user.is_admin()


def is_superadmin(user: Optional[User]) -> bool:
    """Template helper to check if user is superadmin"""
    if not user:
        return False
    return user.is_superadmin()


def is_operator(user: Optional[User]) -> bool:
    """Template helper to check if user is operator or higher"""
    if not user:
        return False
    return user.has_permission(UserRole.OPERATOR)


def can_manage_users(user: Optional[User]) -> bool:
    """Template helper to check if user can manage other users"""
    return is_admin(user)


def can_delete_users(user: Optional[User]) -> bool:
    """Template helper to check if user can delete other users"""
    return is_superadmin(user)


def can_change_user_role(
    current_user: Optional[User], target_user: Optional[User], new_role: UserRole
) -> bool:
    """Template helper to check if current user can change target user's role"""
    if not current_user or not target_user:
        return False

    # Must be admin to change roles
    if not current_user.is_admin():
        return False

    # Can't change own role
    if current_user.id == target_user.id:
        return False

    # Only superadmins can create other superadmins
    if new_role == UserRole.SUPERADMIN and not current_user.is_superadmin():
        return False

    return True


# Dictionary to make these available in templates
TEMPLATE_HELPERS = {
    "has_permission": has_permission,
    "is_admin": is_admin,
    "is_superadmin": is_superadmin,
    "is_operator": is_operator,
    "can_manage_users": can_manage_users,
    "can_delete_users": can_delete_users,
    "can_change_user_role": can_change_user_role,
    "UserRole": UserRole,  # Make the enum available in templates
}
