# Agent Skills - Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the Agent Skills system.

**Estimated Time**: 11-16 hours
**Skill Level**: Intermediate to Advanced

---

## Prerequisites

- ✅ Backend server running (FastAPI + SQLModel)
- ✅ OpenAI API access and credentials
- ✅ Chat agent infrastructure in place
- ✅ Authentication system working
- ✅ Python 3.10+ installed

---

## Phase 1: Core Infrastructure (2-3 hours)

### Step 1.1: Create Skills Package Structure

```bash
cd backend/src
mkdir -p skills/extraction skills/enhancement skills/transformation
```

Create package files:

```bash
# Create __init__.py files
touch skills/__init__.py
touch skills/extraction/__init__.py
touch skills/enhancement/__init__.py
touch skills/transformation/__init__.py
```

### Step 1.2: Implement Base Skill Class

**File**: `backend/src/skills/base.py`

```python
"""
Base class for all agent skills.

Provides common functionality for input/output validation,
error handling, and execution metrics.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional
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
    - execute(): Implementation logic
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
```

### Step 1.3: Create Skill Schemas

**File**: `backend/src/skills/schemas.py`

```python
"""
Input and output schemas for all skills.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Extract Tasks Skill Schemas
# ============================================================================

class ExtractTasksInput(BaseModel):
    """Input schema for extract_tasks skill."""
    text: str = Field(..., min_length=1, description="Text to extract tasks from")
    context: Optional[str] = Field(None, description="Additional context")
    max_tasks: int = Field(10, ge=1, le=50, description="Max tasks to extract")


class ExtractedTask(BaseModel):
    """Single extracted task."""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ExtractTasksOutput(BaseModel):
    """Output schema for extract_tasks skill."""
    tasks: List[ExtractedTask] = Field(..., description="List of extracted tasks")
    count: int = Field(..., description="Total tasks extracted")


# ============================================================================
# Prioritize Task Skill Schemas
# ============================================================================

class PrioritizeTaskInput(BaseModel):
    """Input schema for prioritize_task skill."""
    title: str = Field(..., min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    category: Optional[str] = Field(None, description="Task category")
    context: Optional[str] = Field(None, description="User's workload context")


class PrioritizeTaskOutput(BaseModel):
    """Output schema for prioritize_task skill."""
    priority: Literal["high", "medium", "low"] = Field(..., description="Assigned priority")
    reasoning: str = Field(..., description="Explanation of priority")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


# ============================================================================
# Suggest Schedule Skill Schemas
# ============================================================================

class SuggestScheduleInput(BaseModel):
    """Input schema for suggest_schedule skill."""
    title: str = Field(..., min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[str] = Field(None, description="Task priority")
    category: Optional[str] = Field(None, description="Task category")
    relative_date: Optional[str] = Field(None, description="Relative date (tomorrow, next week)")


class SuggestScheduleOutput(BaseModel):
    """Output schema for suggest_schedule skill."""
    suggested_due_date: datetime = Field(..., description="Suggested due date/time")
    reasoning: str = Field(..., description="Explanation of suggestion")
    time_of_day: Literal["morning", "afternoon", "evening", "specific"] = Field(..., description="Time of day")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


# ============================================================================
# Classify Category Skill Schemas
# ============================================================================

class ClassifyCategoryInput(BaseModel):
    """Input schema for classify_category skill."""
    title: str = Field(..., min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Task description")


class ClassifyCategoryOutput(BaseModel):
    """Output schema for classify_category skill."""
    category: Literal["work", "home", "study", "personal", "shopping", "health", "fitness"] = Field(..., description="Assigned category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Explanation of classification")


# ============================================================================
# Breakdown Task Skill Schemas
# ============================================================================

class BreakdownTaskInput(BaseModel):
    """Input schema for breakdown_task skill."""
    title: str = Field(..., min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    max_subtasks: int = Field(5, ge=2, le=10, description="Max subtasks to generate")


class Subtask(BaseModel):
    """Single subtask."""
    title: str = Field(..., description="Subtask title")
    description: Optional[str] = Field(None, description="Subtask description")
    order: int = Field(..., ge=1, description="Sequence number")
    estimated_duration: Optional[str] = Field(None, description="Estimated time (e.g., '30m', '2h')")


class BreakdownTaskOutput(BaseModel):
    """Output schema for breakdown_task skill."""
    subtasks: List[Subtask] = Field(..., description="List of subtasks")
    total_estimated_duration: Optional[str] = Field(None, description="Total estimated time")
```

### Step 1.4: Implement Skill Registry

**File**: `backend/src/skills/registry.py`

```python
"""
Skill registry for registering and retrieving skills.
"""

from typing import Dict, List, Optional
import logging
from .base import Skill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Central registry for all agent skills.

    Singleton pattern - use get_registry() to access.
    """

    _instance: Optional["SkillRegistry"] = None

    def __init__(self):
        """Initialize the registry."""
        if SkillRegistry._instance is not None:
            raise RuntimeError("SkillRegistry is a singleton. Use get_registry()")
        self._skills: Dict[str, Skill] = {}

    @classmethod
    def get_registry(cls) -> "SkillRegistry":
        """Get or create the global skill registry."""
        if cls._instance is None:
            cls._instance = SkillRegistry()
        return cls._instance

    def register(self, skill: Skill) -> None:
        """
        Register a skill.

        Args:
            skill: Skill instance to register

        Raises:
            ValueError: If skill name already registered
        """
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' is already registered")

        self._skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")

    def get(self, name: str) -> Skill:
        """
        Get skill by name.

        Args:
            name: Skill name

        Returns:
            Skill instance

        Raises:
            KeyError: If skill not found
        """
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' not found in registry")
        return self._skills[name]

    def list_skills(self) -> List[str]:
        """
        List all registered skill names.

        Returns:
            List of skill names
        """
        return list(self._skills.keys())

    def get_all_skills(self) -> Dict[str, Skill]:
        """
        Get all registered skills.

        Returns:
            Dictionary of skill name -> skill instance
        """
        return self._skills.copy()


# Global registry instance
def get_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return SkillRegistry.get_registry()
```

### Step 1.5: Implement Skill Executor

**File**: `backend/src/skills/executor.py`

```python
"""
Skill executor for executing skills with validation.
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
```

---

## Phase 2: Implement Core Skills (4-5 hours)

### Step 2.1: Extract Tasks Skill

**File**: `backend/src/skills/extraction/extract_tasks.py`

```python
"""
Extract Tasks Skill - Extract multiple tasks from natural language text.
"""

from typing import Type
import logging
import json
from openai import AsyncOpenAI
from ..base import Skill, SkillExecutionError
from ..schemas import ExtractTasksInput, ExtractTasksOutput, ExtractedTask
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractTasksSkill(Skill):
    """Extract tasks from natural language text using GPT-4."""

    def __init__(self, openai_client: AsyncOpenAI):
        """
        Initialize the skill.

        Args:
            openai_client: Async OpenAI client
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
            # Build prompt
            system_prompt = """You are a task extraction expert. Extract actionable tasks from text.

Rules:
- Identify action items, todos, and commitments
- Extract task titles (concise, actionable)
- Add optional descriptions if context is available
- Return confidence score for each task (0.0 to 1.0)
- Return JSON with: {tasks: [{title, description, confidence}], count}
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
                tasks=tasks,
                count=len(tasks),
            )

        except json.JSONDecodeError as e:
            raise SkillExecutionError(f"Failed to parse GPT-4 response: {e}")

        except Exception as e:
            raise SkillExecutionError(f"Task extraction failed: {e}")
```

### Step 2.2: Prioritize Task Skill

**File**: `backend/src/skills/enhancement/prioritize_task.py`

```python
"""
Prioritize Task Skill - Assign priority based on keywords, deadlines, context.
"""

from typing import Type
import logging
from datetime import datetime, timezone, timedelta
from ..base import Skill
from ..schemas import PrioritizeTaskInput, PrioritizeTaskOutput
from pydantic import BaseModel

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
        urgent_keywords = ["urgent", "asap", "critical", "important", "immediately", "emergency"]
        low_keywords = ["later", "whenever", "someday", "maybe", "eventually"]

        if any(keyword in text for keyword in urgent_keywords):
            priority = "high"
            reasons.append("Contains urgency keywords")
            confidence = 0.9

        elif any(keyword in text for keyword in low_keywords):
            priority = "low"
            reasons.append("Contains low-priority keywords")
            confidence = 0.85

        # 2. Deadline proximity
        if validated_input.due_date:
            now = datetime.now(timezone.utc)
            time_until_due = validated_input.due_date - now

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

        # Build reasoning
        if not reasons:
            reasons.append("Default priority based on standard rules")

        reasoning = "; ".join(reasons)

        return PrioritizeTaskOutput(
            priority=priority,
            reasoning=reasoning,
            confidence=confidence,
        )
```

*(Continue with Step 2.3-2.5 for remaining skills...)*

---

## Phase 3: API Integration (2-3 hours)

### Step 3.1: Create Skills API Routes

**File**: `backend/src/api/routes/skills.py`

```python
"""
API routes for skill execution.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from ...skills.executor import SkillExecutor
from ...auth.dependencies import get_current_user

router = APIRouter()
executor = SkillExecutor()


class SkillExecuteRequest(BaseModel):
    """Request body for skill execution."""
    input: Dict[str, Any]


class SkillChainRequest(BaseModel):
    """Request body for skill chaining."""
    skills: List[str]
    input: Dict[str, Any]


class BatchSkillRequest(BaseModel):
    """Request body for batch skill operations."""
    task_ids: List[int]


@router.post("/{skill_name}")
async def execute_skill(
    skill_name: str,
    request: SkillExecuteRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Execute a single skill.

    Args:
        skill_name: Name of skill to execute
        request: Skill input data
        user_id: Authenticated user ID

    Returns:
        Skill execution result
    """
    result = await executor.execute(skill_name, request.input, user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/chain")
async def execute_skill_chain(
    request: SkillChainRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Execute multiple skills in sequence.

    Args:
        request: Skill chain configuration
        user_id: Authenticated user ID

    Returns:
        Chain execution result
    """
    # TODO: Implement skill chaining
    pass
```

### Step 3.2: Register Routes

**File**: `backend/src/api/app.py`

```python
# Add to existing imports
from .routes import skills

# Register skills routes
app.include_router(
    skills.router,
    prefix="/api/{user_id}/skills",
    tags=["skills"],
)
```

---

## Phase 4: Chat Agent Integration (1-2 hours)

### Step 4.1: Update Agent System Prompt

**File**: `backend/src/agent/agent.py`

Add to system prompt:

```python
"""
... existing prompt ...

9. **Agent Skills**:
   Use these AI-powered skills to enhance task management:

   - extract_tasks: Extract multiple tasks from text (emails, notes, lists)
   - prioritize_task: Assign priority based on keywords and deadlines
   - suggest_schedule: Suggest optimal due dates and times
   - classify_category: Auto-categorize tasks
   - breakdown_task: Split complex tasks into subtasks

   Invoke skills when appropriate:
   - Multiple tasks in one message → extract_tasks
   - User asks "what's important?" → prioritize_task
   - User asks "when should I do this?" → suggest_schedule
   - No category provided → classify_category
   - Task seems complex → offer to breakdown_task
"""
```

---

## Testing

### Unit Tests

```python
# tests/test_skills.py

async def test_extract_tasks_skill():
    skill = ExtractTasksSkill(openai_client)
    result = await skill.execute({
        "text": "Buy milk and call John",
        "max_tasks": 10
    })
    assert result["success"] == True
    assert len(result["output"]["tasks"]) == 2
```

### Integration Tests

```python
# tests/test_skill_api.py

async def test_skill_execution_endpoint(client, auth_token):
    response = client.post(
        "/api/user123/skills/extract_tasks",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"input": {"text": "Buy milk"}}
    )
    assert response.status_code == 200
```

---

## Deployment Checklist

- [ ] All skills implemented and tested
- [ ] Skill registry initialized on startup
- [ ] API routes registered
- [ ] Agent prompt updated
- [ ] Unit tests passing (80%+ coverage)
- [ ] Integration tests passing
- [ ] Documentation complete
- [ ] OpenAI API key configured
- [ ] Rate limiting enabled
- [ ] Logging and monitoring configured

---

**Total Implementation Time**: 11-16 hours
**Difficulty**: Intermediate to Advanced

---

**Version**: 1.0
**Last Updated**: 2025-12-30
