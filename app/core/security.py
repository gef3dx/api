from passlib.context import CryptContext

from app.core.config import settings

# Create password context based on configuration
pwd_context = CryptContext(schemes=[settings.PASSWORD_HASH_SCHEME], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def is_password_strong(password: str) -> bool:
    """
    Check if a password meets strength requirements.

    Args:
        password: The password to check

    Returns:
        bool: True if password is strong enough, False otherwise
    """
    # Check minimum length
    if len(password) < 8:
        return False

    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return False

    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return False

    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return False

    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False

    return True
