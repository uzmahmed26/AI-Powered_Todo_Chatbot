#!/usr/bin/env python3
"""
Hugging Face Space entry point for Smart Todo ChatKit Backend API.

This file serves as the entry point when deploying to Hugging Face Spaces.
It configures and runs the FastAPI application with production settings.
"""

import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Import the FastAPI app
from src.api.app import app

# Configuration for Hugging Face Spaces
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 7860))  # Hugging Face default port

if __name__ == "__main__":
    print("🚀 Starting Smart Todo ChatKit Backend API")
    print(f"📍 Server running on http://{HOST}:{PORT}")
    print("📚 API Documentation: http://localhost:7860/docs")

    # Check for required environment variables
    required_vars = ["DATABASE_URL", "OPENAI_API_KEY", "JWT_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  WARNING: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set these in Hugging Face Space Settings > Variables and secrets")

    # Run the server
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )
