import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.domain.profiles.models import Profile
from app.domain.users.models import User
from app.main import app

client = TestClient(app)


@pytest.fixture
async def db_session():
    """Create a database session for testing."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    # Create user
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="client",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create profile
    profile = Profile(user_id=user.id)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    return user


def test_get_current_user():
    """Test getting current user."""
    # This would require authentication
    # For now, we'll just test that the endpoint exists
    response = client.get("/api/v1/users/me")

    # This will fail because we're not authenticated
    # but we're testing that the endpoint exists
    assert response.status_code == 401


def test_get_user_by_id(test_user):
    """Test getting user by ID."""
    # This would require authentication and proper permissions
    # For now, we'll just test that the endpoint exists
    response = client.get(f"/api/v1/users/{test_user.id}")

    # This will fail because we're not authenticated
    # but we're testing that the endpoint exists
    assert response.status_code == 401


def test_list_users():
    """Test listing users."""
    # This would require admin authentication
    # For now, we'll just test that the endpoint exists
    response = client.get("/api/v1/users/")

    # This will fail because we're not authenticated
    # but we're testing that the endpoint exists
    assert response.status_code == 401
