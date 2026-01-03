"""
Vercel serverless function entry point for FastAPI backend.

This file serves as the handler for Vercel's Python serverless functions.
It imports the FastAPI app and makes it compatible with Vercel's runtime.
"""

import sys
import os
from pathlib import Path
from mangum import Mangum

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Debug: Log the Python path and environment
print(f"[DEBUG] Python path: {sys.path}")
print(f"[DEBUG] Backend dir: {backend_dir}")
print(f"[DEBUG] APP_ENV: {os.getenv('APP_ENV')}")
print(f"[DEBUG] DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")

try:
    # Import the FastAPI app
    from src.api.app import app

    print("[DEBUG] Successfully imported FastAPI app")

    # Wrap FastAPI with Mangum for Vercel/AWS Lambda compatibility
    handler = Mangum(app, lifespan="off")

except Exception as e:
    # Fallback if imports fail - return detailed error info
    print(f"[ERROR] Failed to import app: {e}")
    print(f"[ERROR] Error type: {type(e).__name__}")

    import traceback
    traceback.print_exc()

    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    fallback_app = FastAPI(title="Phase III Smart Todo API - Error")

    @fallback_app.get("/")
    @fallback_app.get("/health")
    @fallback_app.get("/api/health")
    async def error_handler():
        return JSONResponse(
            status_code=503,
            content={
                "error": "Backend initialization failed",
                "error_type": type(e).__name__,
                "message": str(e),
                "python_path": str(sys.path),
                "backend_dir": str(backend_dir),
                "app_env": os.getenv("APP_ENV"),
                "has_database_url": bool(os.getenv("DATABASE_URL")),
                "hint": "Check Vercel function logs for full traceback"
            }
        )

    handler = Mangum(fallback_app, lifespan="off")
