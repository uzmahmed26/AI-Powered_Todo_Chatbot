"""
OpenAI API client configuration for Phase III Smart Todo ChatKit App.

Provides configured OpenAI client for GPT-4 agent interactions
with proper API key management and error handling.
"""

import os
from typing import Optional
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load .env from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# OpenAI configuration from environment
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
MAX_CONTEXT_MESSAGES: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))

# Validate API key
if not OPENAI_API_KEY:
    logger.warning(
        "OPENAI_API_KEY not found in environment. "
        "OpenAI features will not work until key is provided."
    )


def get_openai_client() -> OpenAI:
    """
    Get configured OpenAI client for synchronous operations.

    Returns:
        Configured OpenAI client

    Raises:
        ValueError: If OPENAI_API_KEY not set in environment
    """
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it in your .env file."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info(f"Initialized OpenAI client with model: {OPENAI_MODEL}")
    return client


def get_async_openai_client() -> AsyncOpenAI:
    """
    Get configured OpenAI client for async operations.

    Returns:
        Configured AsyncOpenAI client

    Raises:
        ValueError: If OPENAI_API_KEY not set in environment
    """
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it in your .env file."
        )

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    logger.info(f"Initialized AsyncOpenAI client with model: {OPENAI_MODEL}")
    return client


def get_model_config() -> dict:
    """
    Get model configuration for OpenAI API calls.

    Returns:
        Dictionary with model configuration (model name, temperature, etc.)
    """
    return {
        "model": OPENAI_MODEL,
        "temperature": OPENAI_TEMPERATURE,
        "max_tokens": 500,  # Reasonable limit for chat responses
    }
