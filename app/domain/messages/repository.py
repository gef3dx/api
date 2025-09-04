import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.messages.models import Message
from app.domain.messages.schemas import MessageCreate


class MessageRepository:
    """Repository for message-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, sender_id: uuid.UUID, message_create: MessageCreate
    ) -> Message:
        """
        Create a new message.

        Args:
            sender_id: The ID of the user sending the message
            message_create: Message creation schema

        Returns:
            Message: The created message
        """
        db_message = Message(
            sender_id=sender_id,
            recipient_id=message_create.recipient_id,
            subject=message_create.subject,
            content=message_create.content,
        )
        self.db.add(db_message)
        await self.db.commit()
        await self.db.refresh(db_message)
        return db_message

    async def get_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """
        Get a message by ID.

        Args:
            message_id: The message ID

        Returns:
            Message: The message or None if not found
        """
        result = await self.db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

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
        result = await self.db.execute(
            select(Message)
            .where((Message.sender_id == user_id) | (Message.recipient_id == user_id))
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

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
        result = await self.db.execute(
            select(Message)
            .where(Message.recipient_id == user_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

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
        result = await self.db.execute(
            select(Message)
            .where(Message.sender_id == user_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, message: Message, **kwargs) -> Message:
        """
        Update a message.

        Args:
            message: The message to update
            **kwargs: Fields to update

        Returns:
            Message: The updated message
        """
        for key, value in kwargs.items():
            setattr(message, key, value)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def delete(self, message: Message) -> None:
        """
        Delete a message.

        Args:
            message: The message to delete
        """
        await self.db.delete(message)
        await self.db.commit()
