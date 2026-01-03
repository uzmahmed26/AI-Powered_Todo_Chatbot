"""
One-time script to initialize database tables in production.

Run this script once after deploying to create all necessary tables.
This should be run locally with your production DATABASE_URL.

Usage:
    python scripts/init_production_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database.engine import init_db, async_engine
from sqlalchemy import text


async def check_tables_exist():
    """Check if tables already exist."""
    async with async_engine.connect() as conn:
        result = await conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
        )
        tables = [row[0] for row in result]
        return tables


async def main():
    """Initialize production database."""
    print("🔍 Checking existing tables...")

    try:
        existing_tables = await check_tables_exist()

        if existing_tables:
            print(f"\n✅ Found {len(existing_tables)} existing tables:")
            for table in existing_tables:
                print(f"   - {table}")

            response = input("\n⚠️  Tables already exist. Recreate them? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted. No changes made.")
                return

        print("\n🚀 Creating database tables...")
        await init_db()

        # Verify tables were created
        new_tables = await check_tables_exist()
        print(f"\n✅ Successfully created {len(new_tables)} tables:")
        for table in new_tables:
            print(f"   - {table}")

        print("\n✨ Database initialization complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        # Clean up
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
