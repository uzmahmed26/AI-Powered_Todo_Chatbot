"""
Test handler - Check backend import
"""
from fastapi import FastAPI
import sys
from pathlib import Path

app = FastAPI()

@app.get("/")
async def test():
    # Test backend import
    backend_dir = Path(__file__).parent.parent / "backend"
    sys.path.insert(0, str(backend_dir))

    try:
        from src.api.app import app as backend_app
        return {
            "status": "success",
            "message": "Backend imported successfully!",
            "routes": len(backend_app.routes),
            "backend_dir": str(backend_dir)
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "python_path": sys.path,
            "backend_dir": str(backend_dir)
        }
