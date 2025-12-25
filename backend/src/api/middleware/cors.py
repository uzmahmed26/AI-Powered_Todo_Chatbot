"""
CORS middleware configuration for Phase III Smart Todo ChatKit App.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.

    Allows frontend from both ports 5173 and 5174.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
