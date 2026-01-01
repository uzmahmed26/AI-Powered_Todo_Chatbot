#!/usr/bin/env python3
"""
Quick start script for Phase III Smart Todo ChatKit App backend.

Run this script to start the FastAPI server:
    python run.py

Or use uvicorn directly:
    uvicorn src.api.app:app --reload --port 8000
"""

import uvicorn
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["DATABASE_URL", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  WARNING: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        print("See .env.example for template\n")

    # Start the server
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
