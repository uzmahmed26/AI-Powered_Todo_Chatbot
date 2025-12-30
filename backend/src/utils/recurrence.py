"""
Recurrence logic utilities for recurring tasks.

This module provides functions for calculating next due dates
for recurring tasks based on their recurrence pattern.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import calendar
import logging

logger = logging.getLogger(__name__)


def calculate_next_due_date(
    current_due_date: Optional[datetime],
    recurrence_pattern: str,
    recurrence_interval: int = 1,
    recurrence_day_of_week: Optional[int] = None,
    recurrence_day_of_month: Optional[int] = None,
) -> datetime:
    """
    Calculate next due date based on recurrence pattern.

    Args:
        current_due_date: Current task due date (None = use tomorrow as base)
        recurrence_pattern: "daily", "weekly", or "monthly"
        recurrence_interval: How often to recur (e.g., every 2 weeks)
        recurrence_day_of_week: Day of week for weekly recurrence (0=Monday, 6=Sunday)
        recurrence_day_of_month: Day of month for monthly recurrence (1-31)

    Returns:
        Next due date as datetime

    Raises:
        ValueError: If recurrence_pattern is invalid

    Examples:
        >>> # Daily recurrence
        >>> next_date = calculate_next_due_date(
        ...     datetime(2025, 12, 30, 9, 0, tzinfo=timezone.utc),
        ...     "daily"
        ... )
        >>> # Returns: 2025-12-31 09:00:00+00:00

        >>> # Weekly recurrence (every Monday)
        >>> next_date = calculate_next_due_date(
        ...     datetime(2025, 12, 30, 17, 0, tzinfo=timezone.utc),
        ...     "weekly",
        ...     recurrence_day_of_week=0
        ... )
        >>> # Returns: next Monday at 17:00

        >>> # Monthly recurrence (1st of month)
        >>> next_date = calculate_next_due_date(
        ...     datetime(2025, 12, 1, 0, 0, tzinfo=timezone.utc),
        ...     "monthly",
        ...     recurrence_day_of_month=1
        ... )
        >>> # Returns: 2026-01-01 00:00:00+00:00
    """

    # If no due date, use tomorrow as default
    if current_due_date is None:
        base_date = datetime.now(timezone.utc) + timedelta(days=1)
        base_date = base_date.replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        base_date = current_due_date

    # Ensure base_date has timezone
    if base_date.tzinfo is None:
        base_date = base_date.replace(tzinfo=timezone.utc)

    # Calculate next date based on pattern
    if recurrence_pattern == "daily":
        next_date = _calculate_daily_recurrence(base_date, recurrence_interval)

    elif recurrence_pattern == "weekly":
        next_date = _calculate_weekly_recurrence(
            base_date, recurrence_interval, recurrence_day_of_week
        )

    elif recurrence_pattern == "monthly":
        next_date = _calculate_monthly_recurrence(
            base_date, recurrence_interval, recurrence_day_of_month
        )

    else:
        raise ValueError(
            f"Invalid recurrence_pattern: {recurrence_pattern}. "
            "Must be 'daily', 'weekly', or 'monthly'"
        )

    logger.info(
        f"Calculated next due date: {next_date} "
        f"(pattern={recurrence_pattern}, interval={recurrence_interval})"
    )

    return next_date


def _calculate_daily_recurrence(base_date: datetime, interval: int) -> datetime:
    """
    Calculate next date for daily recurrence.

    Args:
        base_date: Current due date
        interval: Number of days between recurrences

    Returns:
        Next due date
    """
    return base_date + timedelta(days=interval)


def _calculate_weekly_recurrence(
    base_date: datetime, interval: int, day_of_week: Optional[int]
) -> datetime:
    """
    Calculate next date for weekly recurrence.

    Args:
        base_date: Current due date
        interval: Number of weeks between recurrences
        day_of_week: Target day of week (0=Monday, 6=Sunday), None = simple weekly increment

    Returns:
        Next due date
    """
    if day_of_week is not None:
        # Find next occurrence of specified weekday
        days_ahead = day_of_week - base_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7 * interval
        else:
            # First occurrence is within this week, but if interval > 1,
            # we might need to skip weeks
            if interval > 1:
                # Check if we've already passed this week's occurrence
                # If so, go to next interval
                days_ahead += 7 * (interval - 1)

        next_date = base_date + timedelta(days=days_ahead)
    else:
        # Simple weekly increment (7 * interval days)
        next_date = base_date + timedelta(weeks=interval)

    return next_date


def _calculate_monthly_recurrence(
    base_date: datetime, interval: int, day_of_month: Optional[int]
) -> datetime:
    """
    Calculate next date for monthly recurrence.

    Handles month-end overflow (e.g., Jan 31 → Feb 28/29).

    Args:
        base_date: Current due date
        interval: Number of months between recurrences
        day_of_month: Target day of month (1-31), None = same day as base_date

    Returns:
        Next due date
    """
    # Calculate next month and year
    next_month = base_date.month + interval
    next_year = base_date.year

    while next_month > 12:
        next_month -= 12
        next_year += 1

    # Determine target day
    if day_of_month is not None:
        target_day = day_of_month
    else:
        target_day = base_date.day

    # Handle day overflow (e.g., Feb 31 → Feb 28/29)
    try:
        next_date = base_date.replace(
            year=next_year,
            month=next_month,
            day=target_day
        )
    except ValueError:
        # Day doesn't exist in target month, use last day of month
        last_day = calendar.monthrange(next_year, next_month)[1]
        next_date = base_date.replace(
            year=next_year,
            month=next_month,
            day=last_day
        )
        logger.warning(
            f"Day {target_day} doesn't exist in {next_year}-{next_month:02d}, "
            f"using last day ({last_day})"
        )

    return next_date


def should_create_next_instance(
    recurrence_end_date: Optional[datetime],
    recurrence_active: bool
) -> bool:
    """
    Check if next recurrence instance should be created.

    Args:
        recurrence_end_date: When recurrence should end (None = no end)
        recurrence_active: Whether recurrence is currently active

    Returns:
        True if next instance should be created, False otherwise
    """
    # Check if recurrence is active
    if not recurrence_active:
        logger.info("Recurrence is not active (paused)")
        return False

    # Check if recurrence has ended
    if recurrence_end_date is not None:
        now = datetime.now(timezone.utc)
        if recurrence_end_date.tzinfo is None:
            recurrence_end_date = recurrence_end_date.replace(tzinfo=timezone.utc)

        if now >= recurrence_end_date:
            logger.info(f"Recurrence end date reached: {recurrence_end_date}")
            return False

    return True


def create_next_recurrence_instance(task) -> dict:
    """
    Create data for next recurrence instance from a completed task.

    Args:
        task: Completed Task object with recurrence settings

    Returns:
        Dictionary of task data for new instance

    Example:
        >>> from models.task import Task
        >>> completed_task = Task(...)  # Completed recurring task
        >>> next_task_data = create_next_recurrence_instance(completed_task)
        >>> # Use next_task_data to create new Task in database
    """
    next_due_date = calculate_next_due_date(
        current_due_date=task.due_date,
        recurrence_pattern=task.recurrence_pattern,
        recurrence_interval=task.recurrence_interval,
        recurrence_day_of_week=task.recurrence_day_of_week,
        recurrence_day_of_month=task.recurrence_day_of_month,
    )

    return {
        "user_id": task.user_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "category": task.category,
        "completed": False,  # New task is pending
        "due_date": next_due_date,
        # Recurrence settings copied
        "is_recurring": True,
        "recurrence_pattern": task.recurrence_pattern,
        "recurrence_interval": task.recurrence_interval,
        "recurrence_end_date": task.recurrence_end_date,
        "recurrence_day_of_week": task.recurrence_day_of_week,
        "recurrence_day_of_month": task.recurrence_day_of_month,
        "parent_recurrence_id": task.parent_recurrence_id or task.id,
        "recurrence_active": True,
    }
