"""
Task SQLModel for user todo items.

Represents a task/todo item in the Smart Todo App with user isolation.
All tasks are scoped to user_id for multi-tenant data isolation.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, DateTime, Index
from sqlalchemy.sql import func


class Task(SQLModel, table=True):
    """
    Task model for storing user todo items.

    Attributes:
        id: Auto-incrementing primary key
        user_id: User identifier from Better Auth (for isolation)
        title: Task title (1-200 chars, required)
        description: Optional task description
        completed: Task completion status (default False)
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth")
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)",
    )
    description: Optional[str] = Field(default=None, description="Optional task description")
    completed: bool = Field(default=False, index=True, description="Task completion status")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
        description="Last update timestamp",
    )

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "auth0|abc123",
                "title": "Buy groceries",
                "description": "Milk, bread, eggs",
                "completed": False,
            }
        }


# Create composite index for user-specific task queries
Index("idx_task_user_completed", Task.user_id, Task.completed)
