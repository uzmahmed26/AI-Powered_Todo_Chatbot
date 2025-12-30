"""
Classify Category Skill - Auto-assign category based on task content.

Uses keyword matching to classify tasks into categories.
"""

from typing import Type, Dict, List
import logging
from pydantic import BaseModel

from ..base import Skill
from ..schemas import ClassifyCategoryInput, ClassifyCategoryOutput

logger = logging.getLogger(__name__)


class ClassifyCategorySkill(Skill):
    """Assign task category using keyword matching."""

    # Category keywords mapping
    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        "work": [
            "meeting", "report", "project", "deadline", "presentation",
            "client", "boss", "office", "work", "job", "email", "call",
            "proposal", "review", "document", "spreadsheet", "budget"
        ],
        "shopping": [
            "buy", "purchase", "groceries", "order", "shop", "shopping",
            "store", "market", "amazon", "online", "delivery", "pick up"
        ],
        "health": [
            "doctor", "appointment", "medication", "checkup", "hospital",
            "dentist", "clinic", "medicine", "prescription", "therapy",
            "medical", "health", "exam", "test", "vaccine"
        ],
        "fitness": [
            "gym", "workout", "exercise", "run", "jog", "fitness",
            "training", "sports", "yoga", "pilates", "cardio", "weights"
        ],
        "study": [
            "study", "homework", "assignment", "exam", "test", "class",
            "lecture", "course", "learn", "research", "paper", "essay",
            "read", "textbook", "school", "university", "college"
        ],
        "home": [
            "clean", "fix", "repair", "organize", "laundry", "dishes",
            "vacuum", "maintenance", "house", "apartment", "room"
        ],
    }

    @property
    def name(self) -> str:
        return "classify_category"

    @property
    def description(self) -> str:
        return "Automatically assign a category to a task based on its title and description"

    @property
    def input_schema(self) -> Type[BaseModel]:
        return ClassifyCategoryInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return ClassifyCategoryOutput

    async def _execute(self, validated_input: ClassifyCategoryInput) -> ClassifyCategoryOutput:
        """
        Execute category classification.

        Algorithm:
        1. Combine title and description
        2. Check for keyword matches in each category
        3. Calculate match scores
        4. Return category with highest score
        5. Default to "personal" if no clear match

        Args:
            validated_input: Validated input data

        Returns:
            Category assignment with reasoning
        """
        # Combine title and description
        text = (validated_input.title + " " + (validated_input.description or "")).lower()

        # Calculate scores for each category
        scores: Dict[str, int] = {category: 0 for category in self.CATEGORY_KEYWORDS}
        matched_keywords: Dict[str, List[str]] = {category: [] for category in self.CATEGORY_KEYWORDS}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
                    matched_keywords[category].append(keyword)

        # Find category with highest score
        max_score = max(scores.values())

        if max_score == 0:
            # No keywords matched, default to personal
            return ClassifyCategoryOutput(
                category="personal",
                confidence=0.5,
                reasoning="No specific category keywords found, defaulted to personal"
            )

        # Get category with highest score
        best_category = max(scores, key=scores.get)

        # Calculate confidence based on score
        # Confidence is higher with more keyword matches
        confidence = min(0.7 + (max_score * 0.05), 0.95)

        # Build reasoning
        keywords_str = ", ".join(matched_keywords[best_category][:3])  # Show up to 3 keywords
        reasoning = f"Matched {best_category} keywords: {keywords_str}"

        return ClassifyCategoryOutput(
            category=best_category,
            confidence=confidence,
            reasoning=reasoning,
        )
