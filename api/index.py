"""
Vercel serverless function entry point for FastAPI backend.

Vercel supports ASGI apps natively - just export the FastAPI 'app' variable.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

print(f"[DEBUG] Python path: {sys.path}")
print(f"[DEBUG] Backend dir: {backend_dir}")
print(f"[DEBUG] APP_ENV: {os.getenv('APP_ENV')}")
print(f"[DEBUG] DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")

try:
    # Import the FastAPI app from backend
    from src.api.app import app

    print("[DEBUG] Successfully imported FastAPI app from backend")
    print(f"[DEBUG] App routes count: {len(app.routes)}")

    # Vercel supports ASGI natively - just export 'app'

except Exception as e:
    # Fallback if imports fail
    print(f"[ERROR] Failed to import backend app: {e}")
    print(f"[ERROR] Error type: {type(e).__name__}")

    import traceback
    traceback.print_exc()

    from fastapi import FastAPI

    app = FastAPI(title="Phase III Smart Todo API - Error")

    @app.get("/")
    @app.get("/api/health")
    async def error_handler():
        return {
            "error": "Backend initialization failed",
            "error_type": type(e).__name__,
            "message": str(e),
            "backend_dir": str(backend_dir),
            "app_env": os.getenv("APP_ENV"),
            "has_database_url": bool(os.getenv("DATABASE_URL")),
            "hint": "Check Vercel function logs for full traceback"
        }
