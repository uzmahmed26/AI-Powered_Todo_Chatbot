"""
Vercel serverless function entry point for FastAPI backend.

This file serves as the handler for Vercel's Python serverless functions.
It imports the FastAPI app and makes it compatible with Vercel's runtime.
"""

import sys
from pathlib import Path

# Add the backend/src directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    # Import the FastAPI app
    from src.api.app import app

    # Vercel expects a variable named 'app' or 'handler'
    handler = app

except ImportError as e:
    # Fallback if imports fail - return basic info
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="Phase III Smart Todo API - Error")

    @app.get("/")
    @app.get("/health")
    async def error_handler():
        return JSONResponse(
            status_code=503,
            content={
                "error": "Backend initialization failed",
                "message": str(e),
                "hint": "Check environment variables and dependencies"
            }
        )

    handler = app
