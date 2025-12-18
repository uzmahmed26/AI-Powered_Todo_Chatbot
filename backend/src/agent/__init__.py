"""
AI Agent module for Phase III Smart Todo ChatKit App.

This package provides the OpenAI Agent integration for natural language
understanding, intent recognition, and MCP tool orchestration.
"""

from .agent import TodoAgent
from .client import get_openai_client

__all__ = ["TodoAgent", "get_openai_client"]
