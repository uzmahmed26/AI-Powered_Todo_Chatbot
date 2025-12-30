"""
Skill registry for registering and retrieving skills.

Singleton pattern ensures a single global registry.
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
    def get_instance(cls) -> "SkillRegistry":
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


# Global registry accessor
def get_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return SkillRegistry.get_instance()
