"""
Base class for all agent skills.

Provides common functionality for input/output validation,
error handling, and execution metrics.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel, ValidationError
import logging
import time

logger = logging.getLogger(__name__)


class SkillExecutionError(Exception):
    """Raised when skill execution fails."""
    pass


class Skill(ABC):
    """
    Base class for all agent skills.

    Each skill must define:
    - name: Unique identifier
    - description: What the skill does
    - input_schema: Pydantic model for inputs
    - output_schema: Pydantic model for outputs
    - _execute(): Implementation logic
    """

    def __init__(self):
        """Initialize the skill."""
        self.execution_count = 0
        self.total_execution_time_ms = 0

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the skill does."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Type[BaseModel]:
        """Pydantic schema for input validation."""
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Type[BaseModel]:
        """Pydantic schema for output validation."""
        pass

    @abstractmethod
    async def _execute(self, validated_input: BaseModel) -> BaseModel:
        """
        Execute the skill logic.

        Args:
            validated_input: Validated input data

        Returns:
            Validated output data

        Raises:
            SkillExecutionError: If execution fails
        """
        pass

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill with validation and error handling.

        Args:
            input_data: Raw input dictionary

        Returns:
            Dictionary with success status and output

        Example:
            result = await skill.execute({"text": "Buy milk"})
            # Returns: {"success": True, "output": {...}, "execution_time_ms": 234}
        """
        start_time = time.time()

        try:
            # Validate input
            validated_input = self.input_schema(**input_data)

            logger.info(f"Executing skill: {self.name}")

            # Execute skill logic
            output = await self._execute(validated_input)

            # Validate output
            validated_output = self.output_schema(**output.dict())

            # Update metrics
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.execution_count += 1
            self.total_execution_time_ms += execution_time_ms

            logger.info(
                f"Skill {self.name} executed successfully "
                f"({execution_time_ms}ms)"
            )

            return {
                "success": True,
                "skill": self.name,
                "output": validated_output.dict(),
                "execution_time_ms": execution_time_ms,
            }

        except ValidationError as e:
            logger.error(f"Validation error in skill {self.name}: {e}")
            return {
                "success": False,
                "skill": self.name,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Invalid input: {str(e)}",
                    "details": e.errors(),
                },
            }

        except SkillExecutionError as e:
            logger.error(f"Execution error in skill {self.name}: {e}")
            return {
                "success": False,
                "skill": self.name,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e),
                },
            }

        except Exception as e:
            logger.error(f"Unexpected error in skill {self.name}: {e}", exc_info=True)
            return {
                "success": False,
                "skill": self.name,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get execution metrics for this skill.

        Returns:
            Dictionary with execution count and average time
        """
        avg_time = (
            self.total_execution_time_ms / self.execution_count
            if self.execution_count > 0
            else 0
        )

        return {
            "skill": self.name,
            "execution_count": self.execution_count,
            "total_execution_time_ms": self.total_execution_time_ms,
            "avg_execution_time_ms": int(avg_time),
        }
