import asyncio
import logging

from sqlalchemy import text

from app.db.seeds import seed_database
from app.db.session import Base, async_session_factory, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def apply_schema_migrations(conn) -> None:
    """Ensure newly added columns exist in existing database tables."""
    dialect = conn.dialect.name
    logger.info("Checking and applying schema migrations for dialect: %s", dialect)

    if dialect == "postgresql":
        migration_statements = [
            "ALTER TABLE organisations ADD COLUMN IF NOT EXISTS address VARCHAR(500);",
            "ALTER TABLE organisations ADD COLUMN IF NOT EXISTS phone VARCHAR(100);",
            "ALTER TABLE organisations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);",
            "ALTER TABLE organisations ADD COLUMN IF NOT EXISTS default_language VARCHAR(10) DEFAULT 'ml';",
        ]
        for stmt in migration_statements:
            await conn.execute(text(stmt))
    elif dialect == "sqlite":
        res = await conn.execute(text("PRAGMA table_info(organisations);"))
        existing_cols = {row[1] for row in res.fetchall()}
        if "address" not in existing_cols:
            await conn.execute(text("ALTER TABLE organisations ADD COLUMN address VARCHAR(500);"))
        if "phone" not in existing_cols:
            await conn.execute(text("ALTER TABLE organisations ADD COLUMN phone VARCHAR(100);"))
        if "logo_url" not in existing_cols:
            await conn.execute(text("ALTER TABLE organisations ADD COLUMN logo_url VARCHAR(500);"))
        if "default_language" not in existing_cols:
            await conn.execute(text("ALTER TABLE organisations ADD COLUMN default_language VARCHAR(10) DEFAULT 'ml';"))


async def main() -> None:
    logger.info("Connecting to database and creating schema tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await apply_schema_migrations(conn)
    logger.info("Tables created and schema updated successfully.")

    logger.info("Running database seeds (Organisation, 14 Districts, Platforms, Forms, Settings)...")
    async with async_session_factory() as session:
        await seed_database(session)
    logger.info("Database initialized and seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
