"""
Database engine and session management for Neon Serverless PostgreSQL.

This module provides SQLModel database connectivity with async support,
connection pooling, and proper session management for stateless architecture.
"""

from typing import AsyncGenerator, Optional
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (parent of backend directory)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database configuration
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in .env file (see .env.example for template)"
    )

# Create async engine with connection pooling
# Note: Neon Serverless PostgreSQL works well with connection pooling
# Disable prepared statement cache to avoid schema change issues
connect_args = {
    "prepared_statement_cache_size": 0,  # Disable prepared statement cache
}

# Only require SSL for production (cloud deployments like Neon)
if os.getenv("ENVIRONMENT") != "development":
    connect_args["ssl"] = "require"

async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("APP_ENV") == "development",  # Log SQL in development
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Allow temporary overflow
    connect_args=connect_args,
)

# Create async session factory
async_session_maker = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for FastAPI routes.

    Provides an async database session that automatically commits
    on success and rolls back on exceptions.

    Yields:
        AsyncSession: Database session for query execution

    Example:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_async_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database schema.

    Creates all tables defined in SQLModel models.
    Should be called at application startup.

    Note: In production, use Alembic migrations instead of create_all.
    """
    async with async_engine.begin() as conn:
        # Import all models to ensure they're registered
        from ..models import task, conversation, message  # noqa: F401

        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.

    Should be called at application shutdown to gracefully
    close all database connections in the pool.
    """
    await async_engine.dispose()
