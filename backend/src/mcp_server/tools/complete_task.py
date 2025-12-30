"""
complete_task MCP Tool Implementation

Marks a task as completed and handles recurring task auto-generation.

This tool:
- Validates user_id and task_id
- Marks task as completed
- If recurring, creates next instance automatically
- Returns success with next task info (if applicable)
- Enforces user isolation
"""

from typing import Dict, Any, Optional
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import CompleteTaskInput, CompleteTaskOutput, CompleteTaskData
from ...utils.recurrence import (
    should_create_next_instance,
    create_next_recurrence_instance,
)

logger = logging.getLogger(__name__)


async def execute(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Execute complete_task MCP tool.

    Marks a task as completed. If the task is recurring and active,
    automatically creates the next instance based on recurrence pattern.

    Args:
        user_id: User ID from JWT Auth (required for user isolation)
        task_id: Task ID to mark as completed

    Returns:
        Dictionary with success status, completion data, and message

    Example:
        result = await execute(
            user_id="uuid-123",
            task_id=42
        )
    """
    try:
        # Validate input using Pydantic schema
        input_data = CompleteTaskInput(
            user_id=user_id,
            task_id=task_id,
        )

        logger.info(f"Completing task {task_id} for user {user_id}")

        # Create database session
        async with async_session_maker() as session:
            # Find the task
            stmt = select(Task).where(
                Task.id == input_data.task_id,
                Task.user_id == input_data.user_id
            )
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            # Check if task exists and belongs to user
            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                return {
                    "success": False,
                    "data": None,
                    "message": f"Task {task_id} not found or access denied",
                    "error_code": "NOT_FOUND",
                }

            # Check if already completed
            if task.completed:
                logger.info(f"Task {task_id} already completed")
                return {
                    "success": True,
                    "data": {
                        "task_id": task.id,
                        "status": "completed",
                    },
                    "message": "Task already completed",
                }

            # Mark task as completed
            task.completed = True
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Task {task_id} marked as completed")

            # Check if task is recurring and should create next instance
            next_task_id = None
            next_task_due_date = None

            if task.is_recurring and task.recurrence_pattern:
                if should_create_next_instance(task.recurrence_end_date, task.recurrence_active):
                    try:
                        # Create next recurrence instance
                        next_task_data = create_next_recurrence_instance(task)
                        next_task = Task(**next_task_data)

                        session.add(next_task)
                        await session.commit()
                        await session.refresh(next_task)

                        next_task_id = next_task.id
                        next_task_due_date = next_task.due_date.isoformat() if next_task.due_date else None

                        logger.info(
                            f"Created next recurring instance: task_id={next_task_id}, "
                            f"due_date={next_task_due_date}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to create next recurring instance: {e}", exc_info=True)
                        # Don't fail the completion if recurrence fails
                else:
                    logger.info(f"Recurrence ended or paused for task {task_id}")

            # Build response
            message = "Task completed successfully"
            if next_task_id:
                message = f"Task completed. Next instance created (task_id={next_task_id}, due={next_task_due_date})"
            elif task.is_recurring and not task.recurrence_active:
                message = "Task completed. Recurrence is paused."
            elif task.is_recurring and task.recurrence_end_date:
                message = "Task completed. Recurrence has ended."

            response = {
                "success": True,
                "data": {
                    "task_id": task.id,
                    "status": "completed",
                    "next_task_id": next_task_id,
                    "next_task_due_date": next_task_due_date,
                },
                "message": message,
            }

            return response

    except ValueError as e:
        # Validation error
        logger.warning(f"Validation error in complete_task: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error completing task: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to complete task. Please try again.",
            "error_code": "SERVER_ERROR",
        }
