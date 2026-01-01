"""
Agent Skills Contract

Decorator-based reusable skills for common task management operations.
Backend Python implementation using decorator pattern + registry.
"""

from typing import Callable, Dict, Any, List, TypeVar, Generic
from pydantic import BaseModel
from datetime import datetime, date

# Type variable for generic skill function
T = TypeVar('T')
R = TypeVar('R')


class SkillMetadata(BaseModel):
    """Metadata for registered skill."""
    name: str
    version: str  # Semantic versioning (e.g., "1.0.0")
    description: str
    input_schema: Dict[str, type]
    output_schema: type
    dependencies: List[str] = []  # Other skill names required


class SkillRegistry:
    """Central registry for all agent skills."""

    _registry: Dict[str, SkillMetadata] = {}

    @classmethod
    def register(cls, metadata: SkillMetadata, function: Callable) -> None:
        """Register a skill with metadata."""
        cls._registry[metadata.name] = metadata
        cls._registry[f"{metadata.name}:{metadata.version}"] = metadata
        setattr(metadata, '_function', function)

    @classmethod
    def get(cls, name: str, version: str | None = None) -> Callable | None:
        """Retrieve skill function by name (and optionally version)."""
        key = f"{name}:{version}" if version else name
        metadata = cls._registry.get(key)
        return getattr(metadata, '_function', None) if metadata else None

    @classmethod
    def list_all(cls) -> List[SkillMetadata]:
        """List all registered skills."""
        return [m for k, m in cls._registry.items() if ':' not in k]


def skill(name: str, version: str):
    """
    Decorator to register a function as an agent skill.

    Args:
        name: Unique skill identifier
        version: Semantic version (MAJOR.MINOR.PATCH)

    Returns:
        Decorated function registered in SkillRegistry

    Example:
        @skill(name="task_filtering", version="1.0.0")
        def filter_tasks(tasks: List[Task], filters: FilterCriteria) -> List[Task]:
            '''Filter tasks by status, date, priority.'''
            return [t for t in tasks if meets_criteria(t, filters)]
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        metadata = SkillMetadata(
            name=name,
            version=version,
            description=func.__doc__ or "",
            input_schema=func.__annotations__.copy(),
            output_schema=func.__annotations__.get('return', Any),
            dependencies=[]
        )
        SkillRegistry.register(metadata, func)
        return func
    return decorator


# ============================================================================
# Skill Input/Output Models
# ============================================================================

class FilterCriteria(BaseModel):
    """Criteria for filtering tasks."""
    status: List[str] | None = None  # e.g., ['pending', 'in_progress']
    priority: List[str] | None = None  # e.g., ['high', 'medium']
    due_date_start: date | None = None
    due_date_end: date | None = None
    tags: List[str] | None = None


class DateParseResult(BaseModel):
    """Result of parsing natural language date."""
    parsed_date: date
    confidence: float  # 0.0 - 1.0
    original_text: str
    interpretation: str  # Human-readable explanation


class ValidationResult(BaseModel):
    """Result of input validation."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class TranslatedError(BaseModel):
    """User-friendly error translation."""
    original_error: str
    user_message: str
    language: str  # 'en' or 'ur'
    error_code: str  # Structured error code


# ============================================================================
# Example Skill Contracts
# ============================================================================

@skill(name="task_filtering", version="1.0.0")
def filter_tasks(tasks: List[Dict[str, Any]], filters: FilterCriteria) -> List[Dict[str, Any]]:
    """
    Filter tasks by status, date, priority.

    Args:
        tasks: List of task dictionaries
        filters: Criteria for filtering

    Returns:
        Filtered list of tasks matching all criteria

    Example:
        >>> tasks = [
        ...     {'id': 1, 'title': 'Buy milk', 'status': 'pending', 'priority': 'high'},
        ...     {'id': 2, 'title': 'Walk dog', 'status': 'completed', 'priority': 'low'}
        ... ]
        >>> filters = FilterCriteria(status=['pending'], priority=['high'])
        >>> filter_tasks(tasks, filters)
        [{'id': 1, 'title': 'Buy milk', 'status': 'pending', 'priority': 'high'}]
    """
    ...


@skill(name="date_parsing", version="1.0.0")
def parse_natural_date(text: str, reference_date: date | None = None) -> DateParseResult:
    """
    Parse natural language date expressions.

    Args:
        text: Natural language date (e.g., "tomorrow", "next Friday", "in 3 days")
        reference_date: Base date for relative parsing (defaults to today)

    Returns:
        Parsed date with confidence score

    Example:
        >>> parse_natural_date("tomorrow")
        DateParseResult(
            parsed_date=date(2025, 1, 1),
            confidence=1.0,
            original_text="tomorrow",
            interpretation="Next day after today (2024-12-31)"
        )

        >>> parse_natural_date("next Friday")
        DateParseResult(
            parsed_date=date(2025, 1, 3),
            confidence=0.9,
            original_text="next Friday",
            interpretation="Friday of next week"
        )
    """
    ...


@skill(name="input_validation", version="1.0.0")
def validate_task_input(task_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate task input parameters.

    Args:
        task_data: Task fields to validate (title, description, due_date, priority, etc.)

    Returns:
        Validation result with errors and warnings

    Validation Rules:
        - title: Required, 1-200 characters
        - description: Optional, max 2000 characters
        - due_date: Optional, must be future date
        - priority: Optional, must be in ['low', 'medium', 'high']
        - status: Optional, must be in ['pending', 'in_progress', 'completed']

    Example:
        >>> validate_task_input({'title': '', 'due_date': '2020-01-01'})
        ValidationResult(
            is_valid=False,
            errors=['Title is required', 'Due date must be in the future'],
            warnings=[]
        )
    """
    ...


@skill(name="error_translation", version="1.0.0")
def translate_error(error: str, language: str) -> TranslatedError:
    """
    Translate technical errors to user-friendly messages.

    Args:
        error: Technical error message or exception string
        language: Target language ('en' or 'ur')

    Returns:
        Translated error with user-friendly message

    Example:
        >>> translate_error("DatabaseConnectionError: Connection refused", "en")
        TranslatedError(
            original_error="DatabaseConnectionError: Connection refused",
            user_message="We're having trouble connecting to the server. Please try again in a moment.",
            language="en",
            error_code="DB_CONNECTION_ERROR"
        )

        >>> translate_error("ValidationError: Invalid date format", "ur")
        TranslatedError(
            original_error="ValidationError: Invalid date format",
            user_message="تاریخ کی شکل غلط ہے۔ براہ کرم دوبارہ کوشش کریں۔",
            language="ur",
            error_code="VALIDATION_ERROR"
        )
    """
    ...


# ============================================================================
# Skill Invocation Helpers
# ============================================================================

def invoke_skill(name: str, version: str | None = None, **kwargs) -> Any:
    """
    Invoke a skill by name with keyword arguments.

    Args:
        name: Skill name
        version: Optional specific version (defaults to latest)
        **kwargs: Skill input parameters

    Returns:
        Skill output

    Raises:
        ValueError: If skill not found
        TypeError: If parameters don't match skill signature

    Example:
        >>> result = invoke_skill(
        ...     name="task_filtering",
        ...     tasks=[...],
        ...     filters=FilterCriteria(status=['pending'])
        ... )
    """
    skill_func = SkillRegistry.get(name, version)
    if not skill_func:
        raise ValueError(f"Skill '{name}' not found in registry")

    return skill_func(**kwargs)


def list_available_skills() -> List[SkillMetadata]:
    """
    List all available skills with metadata.

    Returns:
        List of skill metadata

    Example:
        >>> skills = list_available_skills()
        >>> for skill in skills:
        ...     print(f"{skill.name} v{skill.version}: {skill.description}")
        task_filtering v1.0.0: Filter tasks by status, date, priority.
        date_parsing v1.0.0: Parse natural language date expressions.
        ...
    """
    return SkillRegistry.list_all()
