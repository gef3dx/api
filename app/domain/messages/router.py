import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limiter import rate_limit
from app.domain.messages.repository import MessageRepository
from app.domain.messages.schemas import (
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    MessageSendRequest,
    MessageUpdate,
)
from app.domain.messages.service import MessageService
from app.domain.messages.templates import MessageTemplateType, message_template
from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.tasks.message_tasks import send_message_task
from app.utils.exceptions import AppException

router = APIRouter(prefix="/messages", tags=["messages"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_message_service(db: DBSession) -> MessageService:
    """Get message service dependency."""
    message_repo = MessageRepository(db)
    user_repo = UserRepository(db)
    return MessageService(message_repo, user_repo)


@router.post("/", response_model=MessageResponse)
@rate_limit(limit=10, window=60, key_prefix="send_message")
async def send_message(
    message_request: MessageSendRequest,
    current_user: CurrentUser,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    template_type: MessageTemplateType | None = None,
) -> MessageResponse:
    """
    Send a new message.

    Args:
        message_request: Message creation data
        current_user: The current authenticated user
        message_service: The message service
        template_type: Optional template type to use

    Returns:
        MessageResponse: The created message

    Raises:
        HTTPException: If recipient not found
        RateLimitExceededException: If rate limit is exceeded
    """
    try:
        # Use template if provided
        if template_type:
            rendered = message_template.render(
                template_type,
                {
                    "user_name": current_user.username,
                    "notification_title": message_request.subject,
                    "notification_message": message_request.content,
                },
            )
            message_create = MessageCreate(
                recipient_id=message_request.recipient_id,
                subject=rendered["subject"],
                content=rendered["content"],
            )
        else:
            message_create = MessageCreate(
                recipient_id=message_request.recipient_id,
                subject=message_request.subject,
                content=message_request.content,
            )
        # For async processing, call the Celery task directly
        message_dict = message_create.model_dump()
        send_message_task.delay(str(current_user.id), message_dict)

        # For now, we'll still create the message immediately
        # In a full implementation, you might want to return a placeholder
        message = await message_service.send_message(
            uuid.UUID(str(current_user.id)), message_create, sync=True
        )
        return MessageResponse.model_validate(message)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.get("/inbox", response_model=MessageListResponse)
async def get_inbox(
    current_user: CurrentUser,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    skip: int = 0,
    limit: int = 100,
) -> MessageListResponse:
    """
    Get messages received by the current user.

    Args:
        current_user: The current authenticated user
        message_service: The message service
        skip: Number of messages to skip
        limit: Maximum number of messages to return

    Returns:
        MessageListResponse: List of received messages
    """
    messages = await message_service.get_user_inbox(
        uuid.UUID(str(current_user.id)), skip, limit
    )
    total = len(messages)

    # Convert Message objects to MessageResponse objects
    message_responses = [
        MessageResponse.model_validate(message) for message in messages
    ]

    return MessageListResponse(messages=message_responses, total=total)


@router.get("/sent", response_model=MessageListResponse)
async def get_sent_messages(
    current_user: CurrentUser,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    skip: int = 0,
    limit: int = 100,
) -> MessageListResponse:
    """
    Get messages sent by the current user.

    Args:
        current_user: The current authenticated user
        message_service: The message service
        skip: Number of messages to skip
        limit: Maximum number of messages to return

    Returns:
        MessageListResponse: List of sent messages
    """
    messages = await message_service.get_user_sent_messages(
        uuid.UUID(str(current_user.id)), skip, limit
    )
    total = len(messages)

    # Convert Message objects to MessageResponse objects
    message_responses = [
        MessageResponse.model_validate(message) for message in messages
    ]

    return MessageListResponse(messages=message_responses, total=total)


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: uuid.UUID,
    current_user: CurrentUser,
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> MessageResponse:
    """
    Get a specific message.

    Args:
        message_id: The message ID
        current_user: The current authenticated user
        message_service: The message service

    Returns:
        MessageResponse: The requested message

    Raises:
        HTTPException: If message not found or access denied
    """
    try:
        message = await message_service.get_message_by_id(message_id)
        # Check if user is sender or recipient
        if (
            message.sender_id != current_user.id
            and message.recipient_id != current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        return MessageResponse.model_validate(message)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.patch("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: uuid.UUID,
    message_update: MessageUpdate,
    current_user: CurrentUser,
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> MessageResponse:
    """
    Update a message.

    Args:
        message_id: The message ID
        message_update: Message update data
        current_user: The current authenticated user
        message_service: The message service

    Returns:
        MessageResponse: The updated message

    Raises:
        HTTPException: If message not found or access denied
    """
    try:
        # First get the message to check ownership
        message = await message_service.get_message_by_id(message_id)
        if message.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        updated_message = await message_service.update_message(
            message_id, message_update
        )
        return MessageResponse.model_validate(updated_message)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.delete("/{message_id}")
async def delete_message(
    message_id: uuid.UUID,
    current_user: CurrentUser,
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> dict:
    """
    Delete a message.

    Args:
        message_id: The message ID
        current_user: The current authenticated user
        message_service: The message service

    Returns:
        dict: Success message

    Raises:
        HTTPException: If message not found or access denied
    """
    try:
        # First get the message to check ownership
        message = await message_service.get_message_by_id(message_id)
        # Allow deletion by either sender or recipient
        if (
            message.sender_id != current_user.id
            and message.recipient_id != current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")

        await message_service.delete_message(message_id)
        return {"message": "Message deleted successfully"}
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e
