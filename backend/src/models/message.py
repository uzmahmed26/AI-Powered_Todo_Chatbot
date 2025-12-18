"""
Message SQLModel for chat messages within conversations.

Represents individual messages in a conversation thread.
Messages are stored with role (user/assistant) and content.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship, Column, DateTime, Index
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message model for chat messages.

    Attributes:
        id: Auto-incrementing primary key
        conversation_id: Foreign key to conversations table
        user_id: User identifier (for direct queries)
        role: Message sender role (user or assistant)
        content: Message text content (unlimited length)
        created_at: Timestamp when message was sent
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False,
        description="Conversation this message belongs to",
    )
    user_id: str = Field(
        index=True, nullable=False, description="User ID from Better Auth (for queries)"
    )
    role: MessageRole = Field(
        nullable=False, description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(nullable=False, description="Message text content")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Message timestamp",
    )

    # Relationship to conversation (many-to-one)
    # conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "user_id": "auth0|abc123",
                "role": "user",
                "content": "Add buy milk to my tasks",
            }
        }


# Create composite index for efficient message retrieval
Index("idx_message_conversation_created", Message.conversation_id, Message.created_at)
