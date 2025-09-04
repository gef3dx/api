import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.domain.profiles.models import Profile
from app.domain.users.models import User


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="client",
    )
    db_session.add(user)

    # Create profile
    profile = Profile(user_id=user.id)
    db_session.add(profile)

    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(profile)

    return user


def test_register_user(client):
    """Test user registration."""
    # Use a unique email for each test
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_user(client):
    """Test user login."""
    # First register a user with a unique email
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "Password123!",
        },
    )

    # Then login using JSON data (not form data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email_or_username": "loginuser@example.com", "password": "Password123!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_request_password_reset(client):
    """Test password reset request."""
    # First create a user to test with
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "resetuser@example.com",
            "username": "resetuser",
            "password": "Password123!",
        },
    )

    response = client.post(
        "/api/v1/auth/request-password-reset", json={"email": "resetuser@example.com"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_refresh_token(client):
    """Test token refresh."""
    # First register and login to get a refresh token
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "refreshuser@example.com",
            "username": "refreshuser",
            "password": "Password123!",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email_or_username": "refreshuser@example.com",
            "password": "Password123!",
        },
    )

    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Now test refresh token using form data
    response = client.post(
        "/api/v1/auth/refresh", data={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
