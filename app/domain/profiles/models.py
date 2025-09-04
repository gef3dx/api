from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.base import Base


class Profile(Base):
    """User profile model."""

    __tablename__ = "profiles"

    # Shared primary key pattern - user_id is both PK and FK
    user_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
    )
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    timezone = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile", uselist=False)

    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
