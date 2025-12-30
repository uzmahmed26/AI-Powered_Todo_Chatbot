"""
Skill executor for executing skills with validation.

Provides centralized skill execution with error handling and logging.
"""

from typing import Dict, Any
import logging
from .registry import get_registry

logger = logging.getLogger(__name__)


class SkillExecutor:
    """Execute skills with validation and error handling."""

    def __init__(self):
        """Initialize the executor."""
        self.registry = get_registry()

    async def execute(
        self,
        skill_name: str,
        input_data: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Execute a skill.

        Args:
            skill_name: Name of skill to execute
            input_data: Input data dictionary
            user_id: User ID for logging/auditing

        Returns:
            Skill execution result

        Example:
            executor = SkillExecutor()
            result = await executor.execute(
                "extract_tasks",
                {"text": "Buy milk"},
                "user123"
            )
        """
        try:
            # Get skill from registry
            skill = self.registry.get(skill_name)

            logger.info(f"Executing skill '{skill_name}' for user {user_id}")

            # Execute skill
            result = await skill.execute(input_data)

            logger.info(f"Skill '{skill_name}' completed for user {user_id}")

            return result

        except KeyError as e:
            logger.error(f"Skill not found: {e}")
            return {
                "success": False,
                "error": {
                    "code": "SKILL_NOT_FOUND",
                    "message": str(e),
                },
            }

        except Exception as e:
            logger.error(f"Error executing skill: {e}", exc_info=True)
            return {
                "success": False,
                "error": {
                    "code": "EXECUTOR_ERROR",
                    "message": "Failed to execute skill",
                },
            }
