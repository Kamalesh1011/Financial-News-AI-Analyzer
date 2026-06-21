"""Run all agent collection jobs once."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from src.db.mongodb import MongoDB
from src.scheduler.jobs import AgentScheduler


async def main():
    logger.info("Initializing run_once script...")
    db = MongoDB()
    await db.connect()

    scheduler = AgentScheduler()
    results = await scheduler.run_all()
    
    await db.disconnect()
    logger.info("run_once completed!")


if __name__ == "__main__":
    asyncio.run(main())
