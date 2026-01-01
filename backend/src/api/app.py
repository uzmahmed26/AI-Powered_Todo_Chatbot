"""
FastAPI application for Phase III Smart Todo ChatKit App.

This is the main application entry point that:
- Initializes FastAPI with proper configuration
- Configures middleware (CORS, logging, error handling)
- Registers API routes
- Manages database lifecycle (startup/shutdown)
- Provides health check endpoint
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

# Import middleware configuration
from .middleware.cors import configure_cors
from .middleware.error_handler import configure_error_handlers
from .middleware.logging import configure_logging, LoggingMiddleware

# Import database
from ..database.engine import init_db, close_db

# Configure logging first
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database connection
    - Shutdown: Close database connections
    """
    # Startup
    logger.info("Starting Phase III Smart Todo ChatKit App")
    try:
        # Initialize database (creates tables if not exists)
        # Note: In production, use Alembic migrations instead
        # await init_db()
        logger.info("Database initialization skipped (use Alembic migrations)")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Don't fail startup if DB connection fails
        # (allows app to start for health checks)

    # Initialize MCP tools
    try:
        from ..mcp_server.server import register_all_tools

        register_all_tools()
        logger.info("MCP tools registered successfully")
    except Exception as e:
        logger.warning(f"MCP tools registration failed: {e}")
        # Continue startup even if tools fail to register
        # (tools will be registered when implementations are available)

    # Initialize agent skills
    try:
        from ..agent.client import get_async_openai_client
        from ..skills.init_skills import init_skills

        # Get OpenAI client for AI-powered skills
        openai_client = get_async_openai_client()
        init_skills(openai_client)
        logger.info("Agent skills initialized successfully")
    except Exception as e:
        logger.warning(f"Agent skills initialization failed: {e}")
        # Continue startup even if skills fail to initialize

    yield

    # Shutdown
    logger.info("Shutting down Phase III Smart Todo ChatKit App")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Database shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title="Phase III Smart Todo ChatKit API",
    description="AI-powered conversational todo management API with OpenAI Agents SDK and MCP tools",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure middleware (CORS must be last to execute first)
configure_error_handlers(app)
app.add_middleware(LoggingMiddleware)
configure_cors(app)  # Add CORS last so it executes first

logger.info("Middleware configured")


# ============================================================================
# Health Check Endpoint
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns application health status.

    Returns:
        JSON response with health status

    Example:
        GET /health
        Response: {"status": "healthy", "service": "phase3-smart-todo-api"}
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "phase3-smart-todo-api",
            "version": "0.1.0",
        },
    )


# ============================================================================
# API Routes
# ============================================================================

# Import and register chat router
from .routes import chat
from .routes import auth
from .routes import skills
from .routes import tasks

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(skills.router, prefix="/api/{user_id}/skills", tags=["Skills"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])

logger.info("Chat API route registered at /api/{user_id}/chat")
logger.info("Auth API routes registered at /api/auth/*")
logger.info("Skills API routes registered at /api/{user_id}/skills/*")
logger.info("Tasks API routes registered at /api/{user_id}/tasks")


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/", tags=["Root"])
async def root() -> JSONResponse:
    """
    Root endpoint.

    Returns API information.

    Returns:
        JSON response with API info
    """
    return JSONResponse(
        status_code=200,
        content={
            "name": "Phase III Smart Todo ChatKit API",
            "version": "0.1.0",
            "description": "AI-powered conversational todo management",
            "docs": "/docs",
            "health": "/health",
        },
    )


if __name__ == "__main__":
    import uvicorn

    # Run the application
    # Note: In production, use gunicorn + uvicorn workers
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        log_level="info",
    )
