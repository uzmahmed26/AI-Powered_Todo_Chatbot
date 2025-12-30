"""
Breakdown Task Skill - Split complex tasks into smaller, actionable subtasks.

Uses OpenAI GPT-4 to intelligently decompose tasks into logical steps.
"""

from typing import Type
import logging
import json
from pydantic import BaseModel

from ..base import Skill, SkillExecutionError
from ..schemas import BreakdownTaskInput, BreakdownTaskOutput, Subtask

logger = logging.getLogger(__name__)


class BreakdownTaskSkill(Skill):
    """Break down complex tasks into subtasks using GPT-4."""

    def __init__(self, openai_client):
        """
        Initialize the skill.

        Args:
            openai_client: Async OpenAI client instance
        """
        super().__init__()
        self.client = openai_client

    @property
    def name(self) -> str:
        return "breakdown_task"

    @property
    def description(self) -> str:
        return "Break a complex task into smaller, actionable subtasks"

    @property
    def input_schema(self) -> Type[BaseModel]:
        return BreakdownTaskInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return BreakdownTaskOutput

    async def _execute(self, validated_input: BreakdownTaskInput) -> BreakdownTaskOutput:
        """
        Execute task breakdown using GPT-4.

        Args:
            validated_input: Validated input data

        Returns:
            Breakdown with subtasks

        Raises:
            SkillExecutionError: If breakdown fails
        """
        try:
            # Build prompts
            system_prompt = """You are a task planning expert. Break down complex tasks into smaller, actionable subtasks.

Rules:
- Identify logical steps and dependencies
- Create clear, actionable subtask titles
- Order subtasks logically (dependencies first)
- Estimate duration for each subtask if possible (e.g., "30m", "2h", "1d")
- Return JSON with: {subtasks: [{title, description, order, estimated_duration}], total_estimated_duration}

Examples:
Input: "Deploy new feature to production"
Output: {
  "subtasks": [
    {"title": "Run all tests", "description": "Execute unit and integration tests", "order": 1, "estimated_duration": "30m"},
    {"title": "Create pull request", "description": "Open PR with all changes", "order": 2, "estimated_duration": "15m"},
    {"title": "Get code review approval", "description": "Wait for team review", "order": 3, "estimated_duration": "2h"},
    {"title": "Merge to main branch", "description": "Merge approved PR", "order": 4, "estimated_duration": "5m"},
    {"title": "Deploy to production", "description": "Run deployment pipeline", "order": 5, "estimated_duration": "30m"}
  ],
  "total_estimated_duration": "3h20m"
}
"""

            user_prompt = f"""Break down this task into {validated_input.max_subtasks} or fewer subtasks:

Title: "{validated_input.title}"
"""

            if validated_input.description:
                user_prompt += f"\nDescription: {validated_input.description}"

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
            )

            # Parse response
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)

            # Convert to output schema
            subtasks = [
                Subtask(**subtask)
                for subtask in result_json.get("subtasks", [])
            ]

            # Limit to max_subtasks
            subtasks = subtasks[:validated_input.max_subtasks]

            return BreakdownTaskOutput(
                subtasks=subtasks,
                total_estimated_duration=result_json.get("total_estimated_duration"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4 response: {e}")
            raise SkillExecutionError(f"Failed to parse GPT-4 response: {e}")

        except Exception as e:
            logger.error(f"Task breakdown failed: {e}", exc_info=True)
            raise SkillExecutionError(f"Task breakdown failed: {e}")
