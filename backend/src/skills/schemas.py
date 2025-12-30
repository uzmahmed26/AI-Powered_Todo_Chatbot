"""
Input and output schemas for all agent skills.

All schemas use Pydantic for type-safe validation.
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
