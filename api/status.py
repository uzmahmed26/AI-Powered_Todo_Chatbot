"""
Check if backend can be imported
"""
from fastapi import FastAPI
import sys
from pathlib import Path

app = FastAPI()

@app.get("/")
async def check_import():
    # Add backend to path
    backend_dir = Path(__file__).parent.parent / "backend"
    sys.path.insert(0, str(backend_dir))

    try:
        from src.api.app import app as backend_app
        return {
            "status": "success",
            "message": "Backend imported successfully!",
            "routes": len(backend_app.routes)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }
