import uuid
from typing import List

from app.domain.messages.models import Message
from app.domain.messages.repository import MessageRepository
from app.domain.messages.schemas import MessageCreate, MessageUpdate
from app.domain.users.repository import UserRepository
from app.utils.exceptions import NotFoundException


class MessageService:
    """Service for message-related business logic."""

    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def send_message(
        self, sender_id: uuid.UUID, message_create: MessageCreate
    ) -> Message:
        """
        Send a new message.

        Args:
            sender_id: The ID of the user sending the message
            message_create: Message creation schema

        Returns:
            Message: The created message

        Raises:
            NotFoundException: If recipient user not found
        """
        # Check if recipient exists
        recipient = await self.user_repo.get_by_id(message_create.recipient_id)
        if not recipient:
            raise NotFoundException(
                "Recipient user not found",
                {"recipient_id": str(message_create.recipient_id)},
            )

        # Create message
        return await self.message_repo.create(sender_id, message_create)

    async def get_message_by_id(self, message_id: uuid.UUID) -> Message:
        """
        Get a message by ID.

        Args:
            message_id: The message ID

        Returns:
            Message: The message

        Raises:
            NotFoundException: If message not found
        """
        message = await self.message_repo.get_by_id(message_id)
        if not message:
            raise NotFoundException(
                "Message not found", {"message_id": str(message_id)}
            )
        return message

    async def get_user_messages(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get all messages for a user (sent or received).

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of messages
        """
        return await self.message_repo.get_user_messages(user_id, skip, limit)

    async def get_user_inbox(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get messages received by a user.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of received messages
        """
        return await self.message_repo.get_user_inbox(user_id, skip, limit)

    async def get_user_sent_messages(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get messages sent by a user.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of sent messages
        """
        return await self.message_repo.get_user_sent_messages(user_id, skip, limit)

    async def update_message(
        self, message_id: uuid.UUID, message_update: MessageUpdate
    ) -> Message:
        """
        Update a message.

        Args:
            message_id: The message ID
            message_update: Message update schema

        Returns:
            Message: The updated message

        Raises:
            NotFoundException: If message not found
        """
        message = await self.get_message_by_id(message_id)
        update_data = message_update.dict(exclude_unset=True)
        return await self.message_repo.update(message, **update_data)

    async def delete_message(self, message_id: uuid.UUID) -> None:
        """
        Delete a message.

        Args:
            message_id: The message ID

        Raises:
            NotFoundException: If message not found
        """
        message = await self.get_message_by_id(message_id)
        await self.message_repo.delete(message)
