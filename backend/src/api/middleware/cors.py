"""
CORS middleware configuration for Phase III Smart Todo ChatKit App.

Configures Cross-Origin Resource Sharing to allow the frontend
to communicate with the backend API.
"""

import os
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.

    Allows the frontend (running on different origin) to make
    requests to the backend API.

    Args:
        app: FastAPI application instance

    Environment Variables:
        ALLOWED_ORIGINS: Comma-separated list of allowed origins
                        (default: "http://localhost:5173,http://localhost:3000")
    """
    # Get allowed origins from environment
    origins_str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    )

    allowed_origins: List[str] = [origin.strip() for origin in origins_str.split(",")]

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    # Log configured origins (only in development)
    if os.getenv("APP_ENV") == "development":
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"CORS configured with allowed origins: {allowed_origins}")
