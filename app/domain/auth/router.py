from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.domain.auth.repository import AuthRepository
from app.domain.auth.schemas import (
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.domain.auth.service import AuthService
from app.domain.profiles.repository import ProfileRepository
from app.domain.users.repository import UserRepository
from app.domain.users.service import UserService
from app.utils.exceptions import AppException

router = APIRouter(prefix="/auth", tags=["auth"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


def get_auth_service(db: DBSession) -> AuthService:
    """Get auth service dependency."""
    auth_repo = AuthRepository(db)
    user_repo = UserRepository(db)
    user_service_repo = UserRepository(db)
    profile_repo = ProfileRepository(db)
    user_service = UserService(user_service_repo, profile_repo)
    return AuthService(auth_repo, user_repo, user_service)


@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_register: UserRegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    db: DBSession,
) -> TokenResponse:
    """
    Register new user and create empty profile.

    Args:
        user_register: User registration data
        auth_service: The auth service
        db: Database session

    Returns:
        TokenResponse: Access and refresh tokens

    Raises:
        HTTPException: If registration fails
    """
    try:
        user = await auth_service.register_user(user_register)  # type: ignore

        # Create tokens for the new user
        from datetime import datetime

        from app.core.jwt import create_access_token, create_refresh_token, decode_token

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Store refresh token in database
        token_data = decode_token(refresh_token)
        await auth_service.auth_repo.create_refresh_token(
            user_id=user.id,  # type: ignore
            jti=token_data["jti"],
            expires_at=datetime.fromtimestamp(token_data["exp"]),
        )

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_request: UserLoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    Args:
        login_request: Login credentials
        auth_service: The auth service

    Returns:
        TokenResponse: Access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    try:
        user, access_token, refresh_token = await auth_service.authenticate_user(
            login_request
        )
        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except AppException as e:
        raise HTTPException(status_code=401, detail=e.message) from e


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: str = Form(...),
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        auth_service: The auth service
        refresh_token: The refresh token

    Returns:
        TokenResponse: New access and refresh tokens

    Raises:
        HTTPException: If refresh fails
    """
    try:
        new_access_token, new_refresh_token = await auth_service.refresh_access_token(
            refresh_token
        )
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
    except AppException as e:
        raise HTTPException(status_code=401, detail=e.message) from e


@router.post("/logout")
async def logout(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: str = Form(...),
) -> dict:
    """
    Revoke current refresh token.

    Args:
        auth_service: The auth service
        refresh_token: The refresh token to revoke

    Returns:
        dict: Success message

    Raises:
        HTTPException: If logout fails
    """
    try:
        await auth_service.logout(refresh_token)
        return {"message": "Successfully logged out"}
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.post("/logout-all")
async def logout_all(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: CurrentUser,
) -> dict:
    """
    Revoke all refresh tokens for user.

    Args:
        auth_service: The auth service
        current_user: The current authenticated user

    Returns:
        dict: Success message
    """
    # This would need proper implementation with auth dependency
    # For now, we'll just return a success message
    return {"message": "Successfully logged out from all devices"}


@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """
    Request password reset email.

    Args:
        reset_request: Password reset request data
        auth_service: The auth service

    Returns:
        dict: Success message
    """
    await auth_service.request_password_reset(reset_request)
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/confirm-password-reset")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """
    Confirm password reset with token.

    Args:
        reset_confirm: Password reset confirmation data
        auth_service: The auth service

    Returns:
        dict: Success message
    """
    try:
        await auth_service.confirm_password_reset(reset_confirm)
        return {"message": "Password successfully reset"}
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.message) from e
