"""
Task SQLModel for user todo items.

Represents a task/todo item in the Smart Todo App with user isolation.
All tasks are scoped to user_id for multi-tenant data isolation.
"""

from datetime import datetime
from typing import Optional, Literal
from sqlmodel import Field, SQLModel, Column, DateTime, Index
from sqlalchemy.sql import func
from enum import Enum


# Priority and Category Enums
class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskCategory(str, Enum):
    """Task categories."""
    WORK = "work"
    HOME = "home"
    STUDY = "study"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    FITNESS = "fitness"


class Task(SQLModel, table=True):
    """
    Task model for storing user todo items.

    Attributes:
        id: Auto-incrementing primary key
        user_id: User identifier from JWT Auth (for isolation)
        title: Task title (1-200 chars, required)
        description: Optional task description
        completed: Task completion status (default False)
        priority: Task priority (high, medium, low)
        category: Task category (work, home, study, etc.)
        due_date: Optional due date
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from JWT Auth")
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)",
    )
    description: Optional[str] = Field(default=None, description="Optional task description")
    completed: bool = Field(default=False, index=True, description="Task completion status")

    # NEW FIELDS
    priority: str = Field(
        default="medium",
        nullable=False,
        description="Task priority: high, medium, low"
    )
    category: Optional[str] = Field(
        default=None,
        description="Task category: work, home, study, personal, shopping, health, fitness"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Task due date (optional)"
    )

    # RECURRENCE FIELDS
    is_recurring: bool = Field(
        default=False,
        description="Whether this task recurs"
    )
    recurrence_pattern: Optional[str] = Field(
        default=None,
        description="Recurrence pattern: daily, weekly, monthly"
    )
    recurrence_interval: int = Field(
        default=1,
        description="Recurrence interval (e.g., every 2 weeks)"
    )
    recurrence_end_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="When recurrence should end (optional)"
    )
    recurrence_day_of_week: Optional[int] = Field(
        default=None,
        description="Day of week for weekly recurrence (0=Monday, 6=Sunday)"
    )
    recurrence_day_of_month: Optional[int] = Field(
        default=None,
        description="Day of month for monthly recurrence (1-31)"
    )
    parent_recurrence_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id",
        description="Original recurring task template"
    )
    recurrence_active: bool = Field(
        default=True,
        description="Whether recurrence is active (can be paused)"
    )

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
                "user_id": "uuid-string",
                "title": "Buy groceries",
                "description": "Milk, bread, eggs",
                "completed": False,
                "priority": "high",
                "category": "shopping",
                "due_date": "2025-01-15T10:00:00Z",
                "is_recurring": False,
                "recurrence_pattern": None,
                "recurrence_interval": 1
            }
        }


# Create composite index for user-specific task queries
Index("idx_task_user_completed", Task.user_id, Task.completed)
Index("idx_task_user_status_priority", Task.user_id, Task.completed, Task.priority)
