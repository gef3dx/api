import hashlib
import secrets


def generate_jti() -> str:
    """
    Generate a JWT ID (JTI) for token revocation tracking.

    Returns:
        str: A unique JTI string
    """
    return secrets.token_urlsafe(32)


def generate_token() -> str:
    """
    Generate a secure random token.

    Returns:
        str: A secure random token
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """
    Hash a token for secure storage.

    Args:
        token: The token to hash

    Returns:
        str: The hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()
