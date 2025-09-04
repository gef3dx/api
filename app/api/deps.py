import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decode_token
from app.db.session import get_db
from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.utils.exceptions import AuthenticationException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Get current authenticated user dependency.

    Args:
        db: Database session
        token: JWT token

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")  # type: ignore[assignment]
        if user_id is None:
            raise AuthenticationException("Invalid authentication token")

        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise AuthenticationException("User not found")

        if not user.is_active:
            raise AuthenticationException("User account is deactivated")

        return user
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """
    Get user repository dependency.

    Args:
        db: Database session

    Returns:
        UserRepository: User repository
    """
    return UserRepository(db)
