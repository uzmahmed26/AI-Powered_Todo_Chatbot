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

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip()


class TaskData(BaseModel):
    """Task data returned in tool responses."""

    task_id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: str = Field(..., description="Task status (pending/completed)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


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

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None and not v.strip():
            raise ValueError("Task title cannot be empty or whitespace only")
        return v.strip() if v else None


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
