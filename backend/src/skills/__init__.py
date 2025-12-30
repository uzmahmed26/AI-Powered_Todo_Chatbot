"""
Agent Skills Package

Reusable, composable AI skills for task management operations.

Skills are stateless units that perform specific AI-powered operations:
- Extraction: Parse text into structured data (extract_tasks)
- Enhancement: Add intelligence to tasks (prioritize_task, suggest_schedule, classify_category)
- Transformation: Modify task structure (breakdown_task)

Usage:
    from skills.registry import get_registry
    from skills.executor import SkillExecutor

    registry = get_registry()
    executor = SkillExecutor()

    result = await executor.execute("extract_tasks", {"text": "Buy milk"}, "user123")
"""

from .registry import get_registry, SkillRegistry
from .executor import SkillExecutor

__all__ = ["get_registry", "SkillRegistry", "SkillExecutor"]
