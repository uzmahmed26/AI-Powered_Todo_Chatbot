"""
API routes for skill execution.

Provides endpoints for:
- Single skill execution
- Skill listing
- Skill metrics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
import logging

from ...skills.executor import SkillExecutor
from ...skills.registry import get_registry

logger = logging.getLogger(__name__)

router = APIRouter()
executor = SkillExecutor()


class SkillExecuteRequest(BaseModel):
    """Request body for skill execution."""
    input: Dict[str, Any]


class SkillInfo(BaseModel):
    """Skill information response."""
    name: str
    description: str


@router.post("/{skill_name}")
async def execute_skill(
    user_id: str,
    skill_name: str,
    request: SkillExecuteRequest,
):
    """
    Execute a single skill.

    Args:
        user_id: User ID from path parameter
        skill_name: Name of skill to execute
        request: Skill input data

    Returns:
        Skill execution result

    Example:
        POST /api/user123/skills/prioritize_task
        {
          "input": {
            "title": "Fix production bug",
            "category": "work",
            "due_date": "2025-01-02T23:59:59Z"
          }
        }
    """
    try:
        result = await executor.execute(skill_name, request.input, user_id)

        if not result["success"]:
            # Return error details
            raise HTTPException(
                status_code=400,
                detail=result.get("error", {})
            )

        return result

    except KeyError as e:
        logger.error(f"Skill not found: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SKILL_NOT_FOUND",
                "message": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Error executing skill: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to execute skill"
            }
        )


@router.get("/")
async def list_skills(user_id: str):
    """
    List all available skills.

    Args:
        user_id: User ID from path parameter

    Returns:
        List of available skills with descriptions

    Example:
        GET /api/user123/skills/
        Response: {
          "skills": [
            {"name": "extract_tasks", "description": "Extract tasks from text"},
            ...
          ],
          "count": 5
        }
    """
    try:
        registry = get_registry()
        all_skills = registry.get_all_skills()

        skills_info = [
            SkillInfo(name=skill.name, description=skill.description)
            for skill in all_skills.values()
        ]

        return {
            "skills": [s.dict() for s in skills_info],
            "count": len(skills_info)
        }

    except Exception as e:
        logger.error(f"Error listing skills: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to list skills"
            }
        )


@router.get("/{skill_name}/metrics")
async def get_skill_metrics(user_id: str, skill_name: str):
    """
    Get execution metrics for a skill.

    Args:
        user_id: User ID from path parameter
        skill_name: Name of skill

    Returns:
        Skill execution metrics

    Example:
        GET /api/user123/skills/prioritize_task/metrics
        Response: {
          "skill": "prioritize_task",
          "execution_count": 42,
          "total_execution_time_ms": 1234,
          "avg_execution_time_ms": 29
        }
    """
    try:
        registry = get_registry()
        skill = registry.get(skill_name)
        metrics = skill.get_metrics()

        return metrics

    except KeyError as e:
        logger.error(f"Skill not found: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SKILL_NOT_FOUND",
                "message": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to get metrics"
            }
        )
