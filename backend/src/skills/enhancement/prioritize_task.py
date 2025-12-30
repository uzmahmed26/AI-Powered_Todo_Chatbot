"""
Prioritize Task Skill - Assign priority based on keywords, deadlines, context.

Uses heuristic rules to determine task priority without requiring AI models.
"""

from typing import Type
import logging
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from ..base import Skill
from ..schemas import PrioritizeTaskInput, PrioritizeTaskOutput

logger = logging.getLogger(__name__)


class PrioritizeTaskSkill(Skill):
    """Assign task priority using heuristics and keyword analysis."""

    @property
    def name(self) -> str:
        return "prioritize_task"

    @property
    def description(self) -> str:
        return "Intelligently assign priority (high/medium/low) based on keywords, deadlines, and context"

    @property
    def input_schema(self) -> Type[BaseModel]:
        return PrioritizeTaskInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return PrioritizeTaskOutput

    async def _execute(self, validated_input: PrioritizeTaskInput) -> PrioritizeTaskOutput:
        """
        Execute priority assignment.

        Algorithm:
        1. Check for urgency keywords
        2. Check deadline proximity
        3. Apply category-based heuristics
        4. Determine confidence score

        Args:
            validated_input: Validated input data

        Returns:
            Priority assignment with reasoning
        """
        priority = "medium"
        reasons = []
        confidence = 0.7  # Default confidence

        # Combine title and description for analysis
        text = (validated_input.title + " " + (validated_input.description or "")).lower()

        # 1. Keyword analysis
        urgent_keywords = ["urgent", "asap", "critical", "important", "immediately", "emergency", "now"]
        high_keywords = ["deadline", "due soon", "time-sensitive"]
        low_keywords = ["later", "whenever", "someday", "maybe", "eventually", "optional"]

        if any(keyword in text for keyword in urgent_keywords):
            priority = "high"
            reasons.append("Contains urgency keywords")
            confidence = 0.9

        elif any(keyword in text for keyword in high_keywords):
            if priority != "high":
                priority = "high"
            reasons.append("Contains priority keywords")
            confidence = max(confidence, 0.85)

        elif any(keyword in text for keyword in low_keywords):
            priority = "low"
            reasons.append("Contains low-priority keywords")
            confidence = 0.85

        # 2. Deadline proximity
        if validated_input.due_date:
            now = datetime.now(timezone.utc)

            # Ensure due_date is timezone-aware
            due_date = validated_input.due_date
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)

            time_until_due = due_date - now

            if time_until_due < timedelta(hours=24):
                priority = "high"
                reasons.append("Due within 24 hours")
                confidence = 0.95

            elif time_until_due < timedelta(days=3):
                if priority != "high":
                    priority = "medium"
                reasons.append("Due within 3 days")
                confidence = max(confidence, 0.8)

            elif time_until_due > timedelta(days=7):
                if priority == "medium":
                    priority = "low"
                reasons.append("Due in more than 7 days")

        # 3. Category heuristics
        if validated_input.category == "work" and validated_input.due_date:
            if priority == "medium":
                priority = "high"
            reasons.append("Work task with deadline")
            confidence = max(confidence, 0.85)

        elif validated_input.category == "personal" and not validated_input.due_date:
            if priority == "medium":
                priority = "low"
            reasons.append("Personal task without deadline")

        elif validated_input.category == "health":
            if priority != "high":
                priority = "medium"
            reasons.append("Health-related tasks are important")
            confidence = max(confidence, 0.8)

        # Build reasoning
        if not reasons:
            reasons.append("Default priority based on standard rules")

        reasoning = "; ".join(reasons)

        return PrioritizeTaskOutput(
            priority=priority,
            reasoning=reasoning,
            confidence=confidence,
        )
