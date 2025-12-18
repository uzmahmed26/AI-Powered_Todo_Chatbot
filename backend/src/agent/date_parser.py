"""
Natural language date/time parsing for AI Agent.

Parses dates and times from natural language:
- "tomorrow" -> tomorrow's date
- "next Friday" -> next Friday's date
- "in 3 days" -> 3 days from now
- "at 3pm" -> 15:00
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import re


def parse_relative_date(text: str) -> Optional[str]:
    """
    Parse relative date from natural language.

    Args:
        text: Text containing date reference

    Returns:
        ISO date string (YYYY-MM-DD) or None

    Examples:
        "tomorrow" -> "2025-12-19"
        "next friday" -> "2025-12-22" (if today is 2025-12-18)
        "in 3 days" -> "2025-12-21"
    """
    text_lower = text.lower()
    today = datetime.now().date()

    # Tomorrow
    if "tomorrow" in text_lower:
        tomorrow = today + timedelta(days=1)
        return tomorrow.isoformat()

    # Today
    if "today" in text_lower:
        return today.isoformat()

    # In X days
    match = re.search(r"in\s+(\d+)\s+days?", text_lower)
    if match:
        days = int(match.group(1))
        future_date = today + timedelta(days=days)
        return future_date.isoformat()

    # Next week
    if "next week" in text_lower:
        next_week = today + timedelta(days=7)
        return next_week.isoformat()

    # Next [weekday]
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for day_name, day_num in weekdays.items():
        if f"next {day_name}" in text_lower:
            # Calculate days until next occurrence
            current_weekday = today.weekday()
            days_ahead = day_num - current_weekday
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_occurrence = today + timedelta(days=days_ahead)
            return next_occurrence.isoformat()

    return None


def parse_time(text: str) -> Optional[str]:
    """
    Parse time from natural language.

    Args:
        text: Text containing time reference

    Returns:
        Time string (HH:MM) or None

    Examples:
        "at 3pm" -> "15:00"
        "at 9:30am" -> "09:30"
        "at noon" -> "12:00"
    """
    text_lower = text.lower()

    # Noon
    if "noon" in text_lower:
        return "12:00"

    # Midnight
    if "midnight" in text_lower:
        return "00:00"

    # Pattern: "3pm", "3:30pm", "15:00"
    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        meridiem = match.group(3)

        # Convert to 24-hour format if AM/PM specified
        if meridiem == "pm" and hour != 12:
            hour += 12
        elif meridiem == "am" and hour == 12:
            hour = 0

        # Validate
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    return None


def extract_date_time_from_message(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract both date and time from a message.

    Args:
        message: User's message

    Returns:
        Tuple of (date_string, time_string) - both can be None

    Example:
        "Remind me to call mom tomorrow at 3pm"
        -> ("2025-12-19", "15:00")
    """
    date_str = parse_relative_date(message)
    time_str = parse_time(message)

    return (date_str, time_str)
