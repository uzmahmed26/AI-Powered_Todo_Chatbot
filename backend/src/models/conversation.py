"""
Conversation SQLModel for chat conversation threads.

Represents a conversation thread in the Smart Todo ChatKit App.
Each conversation belongs to a user and contains multiple messages.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Column, DateTime
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model for chat threads.

    Attributes:
        id: Auto-incrementing primary key
        user_id: User identifier from Better Auth (for isolation)
        created_at: Timestamp when conversation started
        updated_at: Timestamp when conversation was last active
        messages: Relationship to Message models (one-to-many)
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Conversation start timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
        description="Last activity timestamp",
    )

    # Relationship to messages (one-to-many)
    # messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "auth0|abc123",
            }
        }
