"""
Error handling middleware for Phase III Smart Todo ChatKit App.

Provides centralized error handling with user-friendly error messages
(no stack traces or technical details exposed to users).
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions with user-friendly messages.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    logger.warning(
        f"HTTP {exc.status_code} error on {request.method} {request.url.path}: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": get_error_name(exc.status_code),
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors (Pydantic validation).

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON response with validation error details
    """
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
    )

    # Format validation errors in user-friendly way
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=400,
        content={
            "error": "Bad Request",
            "detail": "; ".join(errors),
            "status_code": 400,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with generic error message
        (no technical details exposed to user)
    """
    logger.error(
        f"Unexpected error on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
        },
    )


def get_error_name(status_code: int) -> str:
    """
    Get user-friendly error name from HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        Error name string
    """
    error_names = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }
    return error_names.get(status_code, "Error")


def configure_error_handlers(app) -> None:
    """
    Configure error handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers configured")
