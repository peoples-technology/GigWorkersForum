import asyncio
import logging

from app.db.seeds import seed_database
from app.db.session import Base, async_session_factory, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def main() -> None:
    logger.info("Connecting to database and creating schema tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully.")

    logger.info("Running database seeds (Organisation, 14 Districts, Platforms, Forms, Settings)...")
    async with async_session_factory() as session:
        await seed_database(session)
    logger.info("Database initialized and seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
