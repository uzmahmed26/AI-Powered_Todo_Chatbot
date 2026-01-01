"""REST API routes for task management."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_, col
import logging
from datetime import datetime

from ...database.engine import get_async_session
from ...models.task import Task
from ...auth.dependencies import get_current_active_user
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tasks"])


@router.get("/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    search: Optional[str] = Query(None, description="Search by title or description"),
    status: Optional[str] = Query(None, description="Filter by status: pending or completed"),
    priority: Optional[str] = Query(None, description="Filter by priority: high, medium, low"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("due_date", description="Sort by: due_date, priority, title"),
    sort_order: str = Query("asc", description="Sort order: asc or desc"),
) -> dict:
    """
    List all tasks for a user with search, filter, and sort.

    Args:
        user_id: User ID
        session: Database session
        current_user: Authenticated user
        search: Search query
        status: Filter by completion status
        priority: Filter by priority level
        category: Filter by category
        sort_by: Sort field
        sort_order: Sort direction

    Returns:
        Dictionary with tasks list
    """
    # Verify user access
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                col(Task.title).ilike(search_pattern),
                col(Task.description).ilike(search_pattern)
            )
        )

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    if priority:
        query = query.where(Task.priority == priority)

    if category:
        query = query.where(Task.category == category)

    # Apply sorting
    if sort_by == "priority":
        # Custom priority order: high > medium > low
        from sqlalchemy import case
        priority_order = case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
            else_=4
        )
        if sort_order == "desc":
            query = query.order_by(priority_order.desc())
        else:
            query = query.order_by(priority_order)
    elif sort_by == "title":
        if sort_order == "desc":
            query = query.order_by(Task.title.desc())
        else:
            query = query.order_by(Task.title)
    else:  # due_date (default)
        # Null dates last
        if sort_order == "desc":
            query = query.order_by(Task.due_date.desc().nullslast())
        else:
            query = query.order_by(Task.due_date.asc().nullslast())

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    # Format tasks
    formatted_tasks = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "category": task.category,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
            "is_recurring": task.is_recurring,
            "recurrence_pattern": task.recurrence_pattern,
            "created_at": task.created_at.isoformat(),
        }
        formatted_tasks.append(task_dict)

    logger.info(f"Retrieved {len(formatted_tasks)} tasks for user {user_id}")

    return {"tasks": formatted_tasks, "count": len(formatted_tasks)}


@router.post("/{user_id}/tasks/{task_id}/complete")
async def complete_task(
    user_id: str,
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """
    Mark a task as complete.

    Args:
        user_id: User ID
        task_id: Task ID to complete
        session: Database session
        current_user: Authenticated user

    Returns:
        Success message
    """
    # Verify user access
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Find task
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Mark as complete
    task.completed = True
    task.updated_at = datetime.utcnow()
    await session.commit()

    logger.info(f"Task {task_id} marked as complete for user {user_id}")

    # Handle recurring tasks
    if task.is_recurring and task.recurrence_pattern:
        from ...utils.recurrence import should_create_next_instance, create_next_recurrence_instance

        if should_create_next_instance(task.recurrence_end_date, task.recurrence_active):
            next_task_data = create_next_recurrence_instance(task)
            next_task = Task(**next_task_data)
            session.add(next_task)
            await session.commit()
            await session.refresh(next_task)

            logger.info(f"Created next recurring task {next_task.id} for user {user_id}")

            return {
                "success": True,
                "message": "Task completed and next instance created",
                "next_task_id": next_task.id,
            }

    return {"success": True, "message": "Task completed successfully"}


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """
    Delete a task.

    Args:
        user_id: User ID
        task_id: Task ID to delete
        session: Database session
        current_user: Authenticated user

    Returns:
        Success message
    """
    # Verify user access
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Find task
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete task
    await session.delete(task)
    await session.commit()

    logger.info(f"Task {task_id} deleted for user {user_id}")

    return {"success": True, "message": "Task deleted successfully"}
