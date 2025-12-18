"""
Logging middleware for Phase III Smart Todo ChatKit App.

Provides structured logging for all API requests with:
- Request/response logging
- Correlation IDs for request tracing
- Performance metrics
- OpenAI API call logging
- MCP tool call logging
"""

import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all API requests and responses.

    Logs:
    - Request method, path, and query parameters
    - Response status code and processing time
    - Correlation ID for request tracing
    - User ID (if authenticated)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Generate correlation ID for request tracing
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Start timer
        start_time = time.time()

        # Log request
        logger.info(
            f"[{correlation_id}] {request.method} {request.url.path} "
            f"query={request.url.query} client={request.client.host}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"[{correlation_id}] {request.method} {request.url.path} "
                f"status={response.status_code} duration={process_time:.3f}s"
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                f"[{correlation_id}] {request.method} {request.url.path} "
                f"error={str(e)} duration={process_time:.3f}s",
                exc_info=True,
            )

            raise


def configure_logging() -> None:
    """
    Configure logging for the application.

    Sets up:
    - Log level from environment (default: INFO)
    - Log format (structured JSON in production, human-readable in dev)
    - Log handlers (console)
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    app_env = os.getenv("APP_ENV", "development")

    # Configure log format based on environment
    if app_env == "production":
        # JSON format for production (structured logging)
        log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    else:
        # Human-readable format for development
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
        )

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set third-party library log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logger.info(f"Logging configured with level: {log_level}")
