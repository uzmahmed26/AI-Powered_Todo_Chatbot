"""
MCP Tool Schemas for Phase III Smart Todo ChatKit App.

Defines input/output schemas for all 5 MCP tools using Pydantic models.
These schemas ensure type-safe tool calling and validation.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ============================================================================
# add_task Tool Schemas
# ============================================================================

class AddTaskInput(BaseModel):
    """Input schema for add_task MCP tool."""

    user_id: str = Field(..., description="User ID from Better Auth (required)")
    title: str = Field(
        ..., min_length=1, max_length=200, description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(None, description="Optional task description")
    priority: str = Field(default="medium", description="Task priority: high, medium, low")
    category: Optional[str] = Field(None, description="Task category")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")

    # Recurrence fields
    is_recurring: bool = Field(default=False, description="Whether this task recurs")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern: daily, weekly, monthly")
    recurrence_interval: int = Field(default=1, ge=1, description="Recurrence interval (e.g., every 2 days)")
    recurrence_end_date: Optional[str] = Field(None, description="When recurrence should end (ISO format)")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of the allowed values."""
        if v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category is one of the allowed values."""
        if v is not None and v not in ["work", "home", "study", "personal", "shopping", "health", "fitness"]:
            raise ValueError("Category must be one of: work, home, study, personal, shopping, health, fitness")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate due_date is a valid ISO datetime string."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("due_date must be a valid ISO datetime string")
        return v

    @field_validator("recurrence_pattern")
    @classmethod
    def validate_recurrence_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate recurrence_pattern is one of the allowed values."""
        if v is not None and v not in ["daily", "weekly", "monthly"]:
            raise ValueError("recurrence_pattern must be one of: daily, weekly, monthly")
        return v

    @field_validator("recurrence_end_date")
    @classmethod
    def validate_recurrence_end_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate recurrence_end_date is a valid ISO datetime string."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("recurrence_end_date must be a valid ISO datetime string")
        return v


class TaskData(BaseModel):
    """Task data returned in tool responses."""

    task_id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status (pending/completed)")
    priority: str = Field(..., description="Task priority (high/medium/low)")
    category: Optional[str] = Field(None, description="Task category")
    due_date: Optional[str] = Field(None, description="Task due date (ISO format)")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    # Recurrence fields
    is_recurring: bool = Field(default=False, description="Whether this task recurs")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    next_recurrence: Optional[str] = Field(None, description="Next recurrence date (if recurring)")


class AddTaskOutput(BaseModel):
    """Output schema for add_task MCP tool."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[TaskData] = Field(None, description="Created task data")
    message: str = Field(..., description="Success or error message")


# ============================================================================
# list_tasks Tool Schemas
# ============================================================================

class ListTasksInput(BaseModel):
    """Input schema for list_tasks MCP tool."""

    user_id: str = Field(..., description="User ID from Better Auth (required)")
    status: Literal["all", "pending", "completed"] = Field(
        "all", description="Filter by status: 'all', 'pending', or 'completed'"
    )
    priority: Optional[str] = Field(None, description="Filter by priority")
    category: Optional[str] = Field(None, description="Filter by category")
    search: Optional[str] = Field(None, description="Search keyword in title/description")
    due_date_from: Optional[str] = Field(None, description="Filter tasks due from this date")
    due_date_to: Optional[str] = Field(None, description="Filter tasks due until this date")
    sort_by: str = Field(default="created_at", description="Sort field: created_at, due_date, priority, title")
    sort_order: str = Field(default="desc", description="Sort order: asc, desc")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority filter."""
        if v is not None and v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category filter."""
        if v is not None and v not in ["work", "home", "study", "personal", "shopping", "health", "fitness"]:
            raise ValueError("Category must be one of: work, home, study, personal, shopping, health, fitness")
        return v

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort_by field."""
        if v not in ["created_at", "due_date", "priority", "title"]:
            raise ValueError("sort_by must be one of: created_at, due_date, priority, title")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort_order."""
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be one of: asc, desc")
        return v


class ListTasksData(BaseModel):
    """Data returned by list_tasks tool."""

    tasks: List[TaskData] = Field(..., description="List of tasks")
    count: int = Field(..., description="Total number of tasks returned")


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks MCP tool."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[ListTasksData] = Field(None, description="Tasks list data")
    message: str = Field(..., description="Success or error message")


# ============================================================================
# complete_task Tool Schemas
# ============================================================================

class CompleteTaskInput(BaseModel):
    """Input schema for complete_task MCP tool."""

    user_id: str = Field(..., description="User ID from Better Auth (required)")
    task_id: int = Field(..., gt=0, description="Task ID to mark as completed")


class CompleteTaskData(BaseModel):
    """Data returned by complete_task tool."""

    task_id: int = Field(..., description="Completed task ID")
    status: str = Field(..., description="Updated status (completed)")


class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task MCP tool."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[CompleteTaskData] = Field(None, description="Completion data")
    message: str = Field(..., description="Success or error message")


# ============================================================================
# delete_task Tool Schemas
# ============================================================================

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task MCP tool."""

    user_id: str = Field(..., description="User ID from Better Auth (required)")
    task_id: int = Field(..., gt=0, description="Task ID to delete")


class DeleteTaskData(BaseModel):
    """Data returned by delete_task tool."""

    task_id: int = Field(..., description="Deleted task ID")
    deleted: bool = Field(..., description="Deletion confirmation")


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task MCP tool."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[DeleteTaskData] = Field(None, description="Deletion data")
    message: str = Field(..., description="Success or error message")


# ============================================================================
# update_task Tool Schemas
# ============================================================================

class UpdateTaskInput(BaseModel):
    """Input schema for update_task MCP tool."""

    user_id: str = Field(..., description="User ID from Better Auth (required)")
    task_id: int = Field(..., gt=0, description="Task ID to update")
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New task title (optional)"
    )
    description: Optional[str] = Field(None, description="New task description (optional)")
    priority: Optional[str] = Field(None, description="Task priority")
    category: Optional[str] = Field(None, description="Task category")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None and not v.strip():
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip() if v else None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority if provided."""
        if v is not None and v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        """Validate category if provided."""
        if v is not None and v not in ["work", "home", "study", "personal", "shopping", "health", "fitness"]:
            raise ValueError("Category must be one of: work, home, study, personal, shopping, health, fitness")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate due_date if provided."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("due_date must be a valid ISO datetime string")
        return v


class UpdateTaskData(BaseModel):
    """Data returned by update_task tool."""

    task_id: int = Field(..., description="Updated task ID")
    title: str = Field(..., description="Updated task title")
    description: Optional[str] = Field(None, description="Updated task description")
    updated_at: datetime = Field(..., description="Update timestamp")


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task MCP tool."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[UpdateTaskData] = Field(None, description="Updated task data")
    message: str = Field(..., description="Success or error message")


# ============================================================================
# Error Response Schema (Common)
# ============================================================================

class MCPErrorResponse(BaseModel):
    """Error response schema for all MCP tools."""

    success: bool = Field(False, description="Always False for errors")
    data: None = Field(None, description="No data on error")
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code (VALIDATION_ERROR, NOT_FOUND, FORBIDDEN, SERVER_ERROR)")
