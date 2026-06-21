"""Initialize MongoDB database indexes."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from src.db.mongodb import MongoDB


async def main():
    """Initialize database."""
    logger.info("Initializing MongoDB...")
    db = MongoDB()
    await db.connect()
    await db.disconnect()
    logger.info("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())