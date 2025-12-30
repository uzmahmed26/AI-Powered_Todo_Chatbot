"""
Extract Tasks Skill - Extract multiple tasks from natural language text.

Uses OpenAI GPT-4 to intelligently parse text and identify actionable tasks.
"""

from typing import Type
import logging
import json
from pydantic import BaseModel

from ..base import Skill, SkillExecutionError
from ..schemas import ExtractTasksInput, ExtractTasksOutput, ExtractedTask

logger = logging.getLogger(__name__)


class ExtractTasksSkill(Skill):
    """Extract tasks from natural language text using GPT-4."""

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
        return "extract_tasks"

    @property
    def description(self) -> str:
        return "Extract one or more tasks from natural language text"

    @property
    def input_schema(self) -> Type[BaseModel]:
        return ExtractTasksInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return ExtractTasksOutput

    async def _execute(self, validated_input: ExtractTasksInput) -> ExtractTasksOutput:
        """
        Execute task extraction using GPT-4.

        Args:
            validated_input: Validated input data

        Returns:
            Extracted tasks

        Raises:
            SkillExecutionError: If extraction fails
        """
        try:
            # Build prompts
            system_prompt = """You are a task extraction expert. Extract actionable tasks from text.

Rules:
- Identify action items, todos, and commitments
- Extract task titles (concise, actionable)
- Add optional descriptions if context is available
- Return confidence score for each task (0.0 to 1.0)
- Return JSON with: {tasks: [{title, description, confidence}], count}

Examples:
Input: "I need to buy milk and call John about the project"
Output: {
  "tasks": [
    {"title": "Buy milk", "description": null, "confidence": 0.95},
    {"title": "Call John about the project", "description": null, "confidence": 0.90}
  ],
  "count": 2
}
"""

            user_prompt = f"""Extract tasks from this text:

"{validated_input.text}"
"""

            if validated_input.context:
                user_prompt += f"\n\nAdditional context: {validated_input.context}"

            user_prompt += f"\n\nExtract up to {validated_input.max_tasks} tasks."

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )

            # Parse response
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)

            # Convert to output schema
            tasks = [
                ExtractedTask(**task)
                for task in result_json.get("tasks", [])
            ]

            return ExtractTasksOutput(
                tasks=tasks[:validated_input.max_tasks],  # Limit to max_tasks
                count=len(tasks[:validated_input.max_tasks]),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT-4 response: {e}")
            raise SkillExecutionError(f"Failed to parse GPT-4 response: {e}")

        except Exception as e:
            logger.error(f"Task extraction failed: {e}", exc_info=True)
            raise SkillExecutionError(f"Task extraction failed: {e}")
