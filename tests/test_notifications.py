import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.models import (
    NotificationStatus,
    NotificationType,
)
from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.schemas import NotificationCreate
from app.domain.notifications.service import NotificationService
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserCreate
from app.main import app

client = TestClient(app)


def test_send_notification_unauthorized():
    """Test sending a notification without authentication."""
    notification_data = {
        "user_id": str(uuid.uuid4()),
        "title": "Test Notification",
        "message": "This is a test notification",
        "type": "info",
    }

    response = client.post("/api/v1/notifications/", json=notification_data)
    assert response.status_code == 401  # Unauthorized without auth


def test_get_my_notifications_unauthorized():
    """Test getting notifications for current user without authentication."""
    response = client.get("/api/v1/notifications/")
    assert response.status_code == 401  # Unauthorized without auth


def test_get_notification_unauthorized():
    """Test getting a specific notification without authentication."""
    notification_id = uuid.uuid4()
    response = client.get(f"/api/v1/notifications/{notification_id}")
    assert response.status_code == 401  # Unauthorized without auth


def test_update_notification_unauthorized():
    """Test updating a notification without authentication."""
    notification_id = uuid.uuid4()
    update_data = {
        "title": "Updated Notification",
        "status": "read",
    }

    response = client.patch(
        f"/api/v1/notifications/{notification_id}", json=update_data
    )
    assert response.status_code == 401  # Unauthorized without auth


def test_delete_notification_unauthorized():
    """Test deleting a notification without authentication."""
    notification_id = uuid.uuid4()
    response = client.delete(f"/api/v1/notifications/{notification_id}")
    assert response.status_code == 401  # Unauthorized without auth


def test_mark_notifications_as_read_unauthorized():
    """Test marking notifications as read without authentication."""
    mark_as_read_data = {
        "notification_ids": [str(uuid.uuid4())],
    }

    response = client.post("/api/v1/notifications/mark-as-read", json=mark_as_read_data)
    assert response.status_code == 401  # Unauthorized without auth


def test_get_my_unread_count_unauthorized():
    """Test getting unread notification count without authentication."""
    response = client.get("/api/v1/notifications/unread-count")
    assert response.status_code == 401  # Unauthorized without auth


@pytest.mark.asyncio
async def test_notification_repository_create(db_session: AsyncSession):
    """Test creating a notification through the repository."""
    # First create a user
    user_repo = UserRepository(db_session)
    user_create = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = await user_repo.create(user_create)

    # Create a notification
    notification_repo = NotificationRepository(db_session)
    notification_create = NotificationCreate(
        user_id=uuid.UUID(str(user.id)),
        title="Test Notification",
        message="This is a test notification",
        type=NotificationType.INFO,
    )
    notification = await notification_repo.create(notification_create)

    assert notification.user_id == user.id
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"
    assert notification.type == NotificationType.INFO
    assert notification.status == NotificationStatus.UNREAD
    assert notification.is_read is False
    assert isinstance(notification.id, uuid.UUID)
    assert isinstance(notification.created_at, datetime)
    assert isinstance(notification.updated_at, datetime)


@pytest.mark.asyncio
async def test_notification_repository_get_by_id(db_session: AsyncSession):
    """Test getting a notification by ID through the repository."""
    # First create a user
    user_repo = UserRepository(db_session)
    user_create = UserCreate(
        email="test2@example.com", username="testuser2", password="testpassword"
    )
    user = await user_repo.create(user_create)

    # Create a notification
    notification_repo = NotificationRepository(db_session)
    notification_create = NotificationCreate(
        user_id=uuid.UUID(str(user.id)),
        title="Test Notification",
        message="This is a test notification",
        type=NotificationType.INFO,
    )
    created_notification = await notification_repo.create(notification_create)

    # Get the notification by ID
    fetched_notification = await notification_repo.get_by_id(
        uuid.UUID(str(created_notification.id))
    )

    assert fetched_notification is not None
    assert fetched_notification.id == created_notification.id
    assert fetched_notification.title == "Test Notification"


@pytest.mark.asyncio
async def test_notification_service_send_notification(db_session: AsyncSession):
    """Test sending a notification through the service."""
    # First create a user
    user_repo = UserRepository(db_session)
    user_create = UserCreate(
        email="test3@example.com", username="testuser3", password="testpassword"
    )
    user = await user_repo.create(user_create)

    # Create notification service
    notification_repo = NotificationRepository(db_session)
    notification_service = NotificationService(notification_repo, user_repo)

    # Send a notification
    notification_create = NotificationCreate(
        user_id=uuid.UUID(str(user.id)),
        title="Service Test Notification",
        message="This is a test notification sent through the service",
        type=NotificationType.SUCCESS,
    )
    notification = await notification_service.send_notification(notification_create)

    assert notification.user_id == user.id
    assert notification.title == "Service Test Notification"
    assert notification.type == NotificationType.SUCCESS
