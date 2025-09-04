import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.domain.messages.models import Message
from app.domain.profiles.models import Profile
from app.domain.users.models import User
from app.main import app

client = TestClient(app)


@pytest.fixture
async def db_session():
    """Create a database session for testing."""
    # This fixture is defined in conftest.py and will be auto-used
    # We're just making it explicit here for clarity
    pass


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


@pytest.fixture
async def test_recipient(db_session: AsyncSession):
    """Create a test recipient user."""
    # Create user
    user = User(
        email="recipient@example.com",
        username="recipient",
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


@pytest.fixture
async def test_message(db_session: AsyncSession, test_user: User, test_recipient: User):
    """Create a test message."""
    message = Message(
        sender_id=test_user.id,
        recipient_id=test_recipient.id,
        subject="Test Message",
        content="This is a test message content",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


def get_auth_headers(user_id: uuid.UUID) -> dict:
    """Generate authorization headers for a user."""
    # In a real implementation, this would generate a valid JWT token
    # For now, we'll just return empty headers as authentication is handled
    # by other mechanisms in the actual app
    return {}


def test_send_message_unauthorized():
    """Test sending a message without authentication."""
    message_data = {
        "recipient_id": str(uuid.uuid4()),
        "subject": "Test Subject",
        "content": "Test Content",
    }
    response = client.post("/api/v1/messages/", json=message_data)
    assert response.status_code == 401


def test_get_inbox_unauthorized():
    """Test getting inbox without authentication."""
    response = client.get("/api/v1/messages/inbox")
    assert response.status_code == 401


def test_get_sent_messages_unauthorized():
    """Test getting sent messages without authentication."""
    response = client.get("/api/v1/messages/sent")
    assert response.status_code == 401


def test_get_message_unauthorized():
    """Test getting a message without authentication."""
    message_id = uuid.uuid4()
    response = client.get(f"/api/v1/messages/{message_id}")
    assert response.status_code == 401


def test_update_message_unauthorized():
    """Test updating a message without authentication."""
    message_id = uuid.uuid4()
    update_data = {"subject": "Updated Subject"}
    response = client.patch(f"/api/v1/messages/{message_id}", json=update_data)
    assert response.status_code == 401


def test_delete_message_unauthorized():
    """Test deleting a message without authentication."""
    message_id = uuid.uuid4()
    response = client.delete(f"/api/v1/messages/{message_id}")
    assert response.status_code == 401


# Note: Authenticated tests would require implementing proper authentication
# in the test client, which would involve creating valid JWT tokens.
# This is typically done by mocking the authentication dependency or
# by using the actual authentication flow in tests.
