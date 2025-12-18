"""
FastAPI application for Phase III Smart Todo ChatKit App.

This package provides the REST API with:
- Stateless chat endpoint
- CORS middleware
- Error handling
- Logging
- Authentication (Better Auth)
"""

from .app import app

__all__ = ["app"]
