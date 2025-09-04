import uuid

from app.domain.users.enums import UserRole
from app.domain.users.models import User
from app.utils.exceptions import AuthorizationException


def check_user_access(current_user: User, target_user_id: uuid.UUID) -> bool:
    """
    Check if current user can access target user.

    Args:
        current_user: The current authenticated user
        target_user_id: The target user ID

    Returns:
        bool: True if access is allowed, False otherwise
    """
    # Admins can access any user
    if current_user.role == UserRole.ADMIN:
        return True

    # Users can access their own data
    if current_user.id == target_user_id:
        return True

    return False


def check_profile_access(current_user: User, target_user_id: uuid.UUID) -> bool:
    """
    Check if current user can access target profile.

    Args:
        current_user: The current authenticated user
        target_user_id: The target user ID

    Returns:
        bool: True if access is allowed, False otherwise
    """
    # Admins can access any profile
    if current_user.role == UserRole.ADMIN:
        return True

    # Users can access their own profile
    if current_user.id == target_user_id:
        return True

    return False


def require_admin_role(current_user: User) -> None:
    """
    Require admin role for access.

    Args:
        current_user: The current authenticated user

    Raises:
        AuthorizationException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationException("Admin role required for this operation")
