"""
add_task MCP Tool Implementation

Creates a new task in the database with user isolation.

This tool:
- Validates input (title 1-200 chars, user_id required)
- Creates Task record in database
- Returns structured success/error response
- Enforces user isolation via user_id
"""

from typing import Dict, Any
import logging
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import AddTaskInput, AddTaskOutput, TaskData, MCPErrorResponse
from ...utils.recurrence import calculate_next_due_date

logger = logging.getLogger(__name__)


async def execute(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",
    category: str = None,
    due_date: str = None,
    is_recurring: bool = False,
    recurrence_pattern: str = None,
    recurrence_interval: int = 1,
    recurrence_end_date: str = None
) -> Dict[str, Any]:
    """
    Execute add_task MCP tool.

    Creates a new task for the specified user with title, description,
    priority, category, optional due date, and recurrence settings.

    Args:
        user_id: User ID from JWT Auth (required for user isolation)
        title: Task title (1-200 characters)
        description: Optional task description
        priority: Task priority (high, medium, low) - defaults to medium
        category: Task category (work, home, study, etc.) - optional
        due_date: Due date in ISO format - optional
        is_recurring: Whether this task recurs (default: False)
        recurrence_pattern: Recurrence pattern: daily, weekly, monthly (optional)
        recurrence_interval: Recurrence interval, e.g., every 2 days (default: 1)
        recurrence_end_date: When recurrence should end in ISO format (optional)

    Returns:
        Dictionary with success status, task data, and message

    Example:
        result = await execute(
            user_id="uuid-123",
            title="Daily standup meeting",
            description="Team sync",
            priority="high",
            category="work",
            due_date="2025-01-02T09:00:00Z",
            is_recurring=True,
            recurrence_pattern="daily",
            recurrence_interval=1
        )
    """
    try:
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "data": None,
                    "message": "Invalid due_date format. Use ISO format (e.g., 2025-01-15T10:00:00Z)",
                    "error_code": "VALIDATION_ERROR",
                }

        # Parse recurrence_end_date if provided
        parsed_recurrence_end_date = None
        if recurrence_end_date:
            try:
                parsed_recurrence_end_date = datetime.fromisoformat(recurrence_end_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "data": None,
                    "message": "Invalid recurrence_end_date format. Use ISO format (e.g., 2025-12-31T23:59:59Z)",
                    "error_code": "VALIDATION_ERROR",
                }

        # Validate input using Pydantic schema
        input_data = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern,
            recurrence_interval=recurrence_interval,
            recurrence_end_date=recurrence_end_date,
        )

        logger.info(f"Creating task for user {user_id}: '{title}' (priority={priority}, category={category}, recurring={is_recurring})")

        # Create database session
        async with async_session_maker() as session:
            # Create new task
            new_task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
                priority=input_data.priority,
                category=input_data.category,
                due_date=parsed_due_date,
                is_recurring=input_data.is_recurring,
                recurrence_pattern=input_data.recurrence_pattern,
                recurrence_interval=input_data.recurrence_interval,
                recurrence_end_date=parsed_recurrence_end_date,
                recurrence_active=True if input_data.is_recurring else False,
            )

            # Add to database
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            logger.info(f"Task created successfully: task_id={new_task.id}")

            # Calculate next recurrence date if task is recurring
            next_recurrence = None
            if new_task.is_recurring and new_task.recurrence_pattern:
                try:
                    next_recurrence_date = calculate_next_due_date(
                        current_due_date=new_task.due_date,
                        recurrence_pattern=new_task.recurrence_pattern,
                        recurrence_interval=new_task.recurrence_interval,
                    )
                    next_recurrence = next_recurrence_date.isoformat()
                except Exception as e:
                    logger.warning(f"Failed to calculate next recurrence: {e}")

            # Build response data
            result = {
                "success": True,
                "data": {
                    "task_id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "status": "pending" if not new_task.completed else "completed",
                    "priority": new_task.priority,
                    "category": new_task.category,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                    "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
                    "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None,
                    "is_recurring": new_task.is_recurring,
                    "recurrence_pattern": new_task.recurrence_pattern,
                    "next_recurrence": next_recurrence,
                },
                "message": "Task created successfully" + (" (recurring)" if new_task.is_recurring else ""),
            }

            return result

    except ValueError as e:
        # Validation error
        logger.warning(f"Validation error in add_task: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error creating task: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to create task. Please try again.",
            "error_code": "SERVER_ERROR",
        }
