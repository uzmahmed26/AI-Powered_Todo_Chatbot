"""
Agent Skills Module

Reusable skills for common task management patterns using decorator pattern.
Skills are registered in SKILL_REGISTRY and can be invoked by name.
"""

from .registry import skill, SKILL_REGISTRY, invoke_skill, list_available_skills, get_registry

__all__ = [
    'skill',
    'SKILL_REGISTRY',
    'invoke_skill',
    'list_available_skills',
    'get_registry',
]
