"""
Vercel serverless function entry point for FastAPI backend.

This file serves as the handler for Vercel's Python serverless functions.
It imports the FastAPI app and makes it compatible with Vercel's runtime.
"""

import sys
from pathlib import Path

# Add the backend/src directory to the Python path
# This allows imports from src.api.app to work correctly
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from src.api.app import app

# Vercel expects a variable named 'app' or a handler function
# Since we're using FastAPI, we can directly export the app
# The app will be wrapped by Vercel's Python runtime
handler = app
