"""Seed default watchlist symbols."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from src.db.mongodb import MongoDB
from src.db.repositories import WatchlistRepository
from config.constants import DEFAULT_WATCHLIST


async def main():
    """Seed watchlist."""
    logger.info("Seeding watchlist...")
    db = MongoDB()
    await db.connect()

    repo = WatchlistRepository()
    count = 0
    for item in DEFAULT_WATCHLIST:
        existing = await repo.find_one({"symbol": item["symbol"]})
        if not existing:
            await repo.add_to_watchlist(
                symbol=item["symbol"],
                asset_type=item["asset_type"],
                alert_on=item["alert_on"],
            )
            count += 1
            logger.info(f"Added {item['symbol']} to watchlist")

    await db.disconnect()
    logger.info(f"Watchlist seeded: {count} new symbols added")


if __name__ == "__main__":
    asyncio.run(main())