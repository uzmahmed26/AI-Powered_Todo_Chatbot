"""
Suggest Schedule Skill - Suggest optimal due dates and times.

Uses heuristics for time-of-day suggestions and relative date parsing.
"""

from typing import Type, Dict, Tuple
import logging
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from ..base import Skill
from ..schemas import SuggestScheduleInput, SuggestScheduleOutput

logger = logging.getLogger(__name__)


class SuggestScheduleSkill(Skill):
    """Suggest optimal due dates and times based on task characteristics."""

    # Time-of-day keywords mapping
    TIME_KEYWORDS: Dict[str, Tuple[int, str]] = {
        # Format: keyword -> (hour, time_of_day)
        "standup": (9, "morning"),
        "meeting": (10, "morning"),
        "email": (9, "morning"),
        "review": (17, "evening"),
        "plan": (18, "evening"),
        "prepare": (19, "evening"),
        "call": (14, "specific"),
        "appointment": (14, "specific"),
    }

    # Category default times
    CATEGORY_DEFAULTS: Dict[str, Tuple[int, str]] = {
        "work": (9, "morning"),
        "personal": (18, "evening"),
        "shopping": (14, "afternoon"),
        "health": (10, "morning"),
        "fitness": (7, "morning"),
        "study": (14, "afternoon"),
        "home": (16, "afternoon"),
    }

    @property
    def name(self) -> str:
        return "suggest_schedule"

    @property
    def description(self) -> str:
        return "Suggest optimal due date and time for a task based on title, description, and user's schedule"

    @property
    def input_schema(self) -> Type[BaseModel]:
        return SuggestScheduleInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return SuggestScheduleOutput

    def _parse_relative_date(self, relative_date: str) -> datetime:
        """
        Parse relative date strings to absolute datetime.

        Args:
            relative_date: String like "tomorrow", "next week", "in 3 days"

        Returns:
            Absolute datetime
        """
        now = datetime.now(timezone.utc)
        relative_lower = relative_date.lower().strip()

        # Parse common patterns
        if relative_lower in ["today", "tonight"]:
            return now.replace(hour=23, minute=59, second=0, microsecond=0)

        elif relative_lower == "tomorrow":
            return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)

        elif relative_lower in ["next week", "1 week"]:
            return (now + timedelta(weeks=1)).replace(hour=12, minute=0, second=0, microsecond=0)

        elif relative_lower == "next month":
            # Add 30 days as approximation
            return (now + timedelta(days=30)).replace(hour=12, minute=0, second=0, microsecond=0)

        elif "day" in relative_lower:
            # Extract number of days
            import re
            match = re.search(r'(\d+)\s*day', relative_lower)
            if match:
                days = int(match.group(1))
                return (now + timedelta(days=days)).replace(hour=12, minute=0, second=0, microsecond=0)

        # Default: tomorrow
        return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)

    def _suggest_time_of_day(self, title: str, category: str = None) -> Tuple[int, str]:
        """
        Suggest time of day based on title and category.

        Args:
            title: Task title
            category: Task category

        Returns:
            Tuple of (hour, time_of_day_label)
        """
        title_lower = title.lower()

        # Check for specific keywords
        for keyword, (hour, time_label) in self.TIME_KEYWORDS.items():
            if keyword in title_lower:
                return (hour, time_label)

        # Use category defaults
        if category and category in self.CATEGORY_DEFAULTS:
            return self.CATEGORY_DEFAULTS[category]

        # Default: afternoon
        return (14, "afternoon")

    async def _execute(self, validated_input: SuggestScheduleInput) -> SuggestScheduleOutput:
        """
        Execute schedule suggestion.

        Algorithm:
        1. Parse relative date if provided
        2. Determine time of day based on keywords and category
        3. Combine date and time
        4. Build reasoning

        Args:
            validated_input: Validated input data

        Returns:
            Schedule suggestion with reasoning
        """
        # 1. Determine base date
        if validated_input.relative_date:
            base_date = self._parse_relative_date(validated_input.relative_date)
            date_reason = f"Parsed '{validated_input.relative_date}'"
        else:
            # Default: tomorrow
            base_date = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
                hour=12, minute=0, second=0, microsecond=0
            )
            date_reason = "Default: tomorrow"

        # 2. Determine time of day
        hour, time_label = self._suggest_time_of_day(
            validated_input.title,
            validated_input.category
        )

        # 3. Combine date and time
        suggested_date = base_date.replace(hour=hour, minute=0, second=0, microsecond=0)

        # 4. Build reasoning
        reasons = [date_reason]

        if time_label == "morning":
            reasons.append("Morning tasks are best for focus and productivity")
        elif time_label == "afternoon":
            reasons.append("Afternoon is suitable for general tasks")
        elif time_label == "evening":
            reasons.append("Evening is good for planning and review")
        elif time_label == "specific":
            reasons.append("Specific time suggested based on task type")

        if validated_input.category:
            reasons.append(f"{validated_input.category} tasks typically scheduled in {time_label}")

        reasoning = "; ".join(reasons)

        # 5. Determine confidence
        # Higher confidence if we found specific keywords
        title_lower = validated_input.title.lower()
        has_time_keyword = any(keyword in title_lower for keyword in self.TIME_KEYWORDS.keys())
        confidence = 0.85 if has_time_keyword else 0.75

        return SuggestScheduleOutput(
            suggested_due_date=suggested_date,
            reasoning=reasoning,
            time_of_day=time_label,
            confidence=confidence,
        )
