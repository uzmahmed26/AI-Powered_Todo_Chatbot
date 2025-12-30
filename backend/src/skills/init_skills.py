"""
Initialize and register all agent skills.

This module is called on application startup to register all skills
with the skill registry.
"""

import logging
from .registry import get_registry
from .enhancement.prioritize_task import PrioritizeTaskSkill
from .enhancement.classify_category import ClassifyCategorySkill
from .enhancement.suggest_schedule import SuggestScheduleSkill
from .extraction.extract_tasks import ExtractTasksSkill
from .transformation.breakdown_task import BreakdownTaskSkill

logger = logging.getLogger(__name__)


def init_skills(openai_client=None) -> None:
    """
    Initialize and register all skills.

    Args:
        openai_client: Async OpenAI client (required for extract_tasks and breakdown_task)

    Note:
        This function should be called once during application startup.
    """
    registry = get_registry()

    logger.info("Initializing agent skills...")

    # Register heuristic-based skills (no OpenAI required)
    try:
        registry.register(PrioritizeTaskSkill())
        registry.register(ClassifyCategorySkill())
        registry.register(SuggestScheduleSkill())
        logger.info("Registered 3 heuristic-based skills")
    except Exception as e:
        logger.error(f"Failed to register heuristic skills: {e}")

    # Register AI-powered skills (require OpenAI client)
    if openai_client:
        try:
            registry.register(ExtractTasksSkill(openai_client))
            registry.register(BreakdownTaskSkill(openai_client))
            logger.info("Registered 2 AI-powered skills")
        except Exception as e:
            logger.error(f"Failed to register AI-powered skills: {e}")
    else:
        logger.warning(
            "OpenAI client not provided. AI-powered skills "
            "(extract_tasks, breakdown_task) will not be available."
        )

    logger.info(f"Total skills registered: {len(registry.list_skills())}")
    logger.info(f"Available skills: {', '.join(registry.list_skills())}")
