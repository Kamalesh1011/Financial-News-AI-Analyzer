"""Async MongoDB client with Motor driver - serverless compatible."""
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from loguru import logger

from config.settings import settings


_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance with lazy connection (serverless compatible)."""
    global _client, _database

    if _database is not None:
        return _database

    logger.info("Connecting to MongoDB...")
    try:
        _client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=50,
            minPoolSize=0,
        )
        _database = _client[settings.mongodb_db]

        # Verify connection
        await _client.admin.command("ping")
        logger.info(f"Connected to MongoDB: {settings.mongodb_db}")

        return _database

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def collection(name: str):
    """Get collection by name (async - call get_database() first)."""
    return _database[name] if _database else None


class MongoDB:
    """Async MongoDB client - serverless compatible wrapper."""

    @staticmethod
    async def connect() -> None:
        """Establish connection to MongoDB."""
        await get_database()

    @staticmethod
    async def disconnect() -> None:
        """Close MongoDB connection."""
        global _client, _database
        if _client is not None:
            _client.close()
            _client = None
            _database = None
            logger.info("Disconnected from MongoDB")

    @staticmethod
    async def ping() -> bool:
        """Check MongoDB connection health."""
        try:
            db = await get_database()
            await db.command("ping")
            return True
        except Exception:
            return False

    @staticmethod
    async def get_stats() -> Dict[str, Any]:
        """Get database statistics."""
        try:
            db = await get_database()
            stats = await db.command("dbStats")
            collections = await db.list_collection_names()
            return {
                "database": settings.mongodb_db,
                "collections": collections,
                "documents": stats.get("objects", 0),
                "storage_size_mb": round(stats.get("storageSize", 0) / (1024 * 1024), 2),
                "data_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
            }
        except Exception as e:
            logger.error(f"Failed to get MongoDB stats: {e}")
            return {}

    @staticmethod
    async def get_database() -> AsyncIOMotorDatabase:
        """Get database instance."""
        return await get_database()
