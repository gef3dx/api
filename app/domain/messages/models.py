import uuid

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.base import Base


class Message(Base):
    """User message model."""

    __tablename__ = "messages"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    recipient_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship(
        "User", foreign_keys=[recipient_id], backref="received_messages"
    )

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id}, subject='{self.subject}')>"
