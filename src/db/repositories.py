"""Data access repositories for MongoDB collections."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from .mongodb import get_database
from .models import (
    RawNewsDocument,
    MarketDataDocument,
    SentimentAnalysisDocument,
    ImpactAnalysisDocument,
    AlertDocument,
    WatchlistDocument,
    UserDocument,
)
from config.constants import COLLECTION_NAMES


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Get collection with lazy connection."""
        db = await get_database()
        return db[self.collection_name]

    async def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a single document."""
        collection = await self._get_collection()
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents."""
        if not documents:
            return []
        collection = await self._get_collection()
        result = await collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    async def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        collection = await self._get_collection()
        return await collection.find_one(filter)

    async def find_many(
        self,
        filter: Dict[str, Any] = None,
        sort: List[tuple] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents."""
        if filter is None:
            filter = {}

        collection = await self._get_collection()
        cursor = collection.find(filter)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)

        return await cursor.to_list(length=limit)

    async def update_one(
        self, filter: Dict[str, Any], update: Dict[str, Any], upsert: bool = False
    ) -> bool:
        """Update a single document."""
        collection = await self._get_collection()
        result = await collection.update_one(filter, update, upsert=upsert)
        return result.modified_count > 0 or result.upserted_id is not None

    async def update_many(self, filter: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update multiple documents."""
        collection = await self._get_collection()
        result = await collection.update_many(filter, update)
        return result.modified_count

    async def delete_one(self, filter: Dict[str, Any]) -> bool:
        """Delete a single document."""
        collection = await self._get_collection()
        result = await collection.delete_one(filter)
        return result.deleted_count > 0

    async def count(self, filter: Dict[str, Any] = None) -> int:
        """Count documents matching filter."""
        collection = await self._get_collection()
        return await collection.count_documents(filter or {})

    async def exists(self, filter: Dict[str, Any]) -> bool:
        """Check if document exists."""
        collection = await self._get_collection()
        return await collection.count_documents(filter, limit=1) > 0


class NewsRepository(BaseRepository):
    """Repository for raw news articles."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES["raw_news"])

    async def exists_by_url(self, url: str) -> bool:
        """Check if news article exists by URL."""
        return await self.exists({"url": url})

    async def exists_by_external_id(self, source: str, external_id: str) -> bool:
        """Check if news article exists by external ID."""
        return await self.exists({"source": source, "external_id": external_id})

    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent news articles."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={
                "$or": [
                    {"created_at": {"$gte": since}},
                    {"published_at": {"$gte": since}}
                ]
            },
            sort=[("published_at", -1)],
            limit=limit,
        )

    async def get_by_ticker(self, ticker: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get news articles mentioning a specific ticker."""
        return await self.find_many(
            filter={"tickers": ticker},
            sort=[("published_at", -1)],
            limit=limit,
        )

    async def get_unprocessed(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get news articles without sentiment analysis."""
        collection = await self._get_collection()
        pipeline = [
            {
                "$addFields": {
                    "id_str": {"$toString": "$_id"}
                }
            },
            {
                "$lookup": {
                    "from": "sentiment_analysis",
                    "localField": "id_str",
                    "foreignField": "news_id",
                    "as": "sentiment",
                }
            },
            {"$match": {"sentiment": {"$size": 0}}},
            {"$sort": {"created_at": -1}},
            {"$limit": limit},
        ]
        return await collection.aggregate(pipeline).to_list(length=limit)

    async def get_with_sentiment(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get news articles with sentiment analysis."""
        collection = await self._get_collection()
        pipeline = [
            {
                "$addFields": {
                    "id_str": {"$toString": "$_id"}
                }
            },
            {
                "$lookup": {
                    "from": "sentiment_analysis",
                    "localField": "id_str",
                    "foreignField": "news_id",
                    "as": "sentiment",
                }
            },
            {"$unwind": {"path": "$sentiment", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"created_at": -1}},
            {"$limit": limit},
        ]
        return await collection.aggregate(pipeline).to_list(length=limit)


class MarketDataRepository(BaseRepository):
    """Repository for market data snapshots."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES["market_data"])

    async def get_latest(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest market data for a symbol."""
        return await self.find_one(
            filter={"symbol": symbol},
            sort=[("timestamp", -1)],
        )

    async def get_latest_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get latest market data for multiple symbols."""
        collection = await self._get_collection()
        pipeline = [
            {"$match": {"symbol": {"$in": symbols}}},
            {"$sort": {"timestamp": -1}},
            {"$group": {"_id": "$symbol", "doc": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$doc"}},
        ]
        return await collection.aggregate(pipeline).to_list(length=len(symbols))

    async def get_history(
        self, symbol: str, hours: int = 24, source: str = None
    ) -> List[Dict[str, Any]]:
        """Get historical market data for a symbol."""
        since = datetime.utcnow() - timedelta(hours=hours)
        query = {"symbol": symbol, "timestamp": {"$gte": since}}
        if source:
            query["source"] = source
        return await self.find_many(
            filter=query,
            sort=[("timestamp", 1)],
        )

    async def get_all_symbols(self) -> List[str]:
        """Get all unique symbols in market data."""
        collection = await self._get_collection()
        return await collection.distinct("symbol")

    async def get_price_history(
        self, symbol: str, hours: int = 72
    ) -> List[Dict[str, Any]]:
        """Get price history for charts."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={"symbol": symbol, "timestamp": {"$gte": since}},
            sort=[("timestamp", 1)],
        )

    async def get_correlation_matrix(
        self, symbols: List[str], hours: int = 72
    ) -> Dict[str, Any]:
        """Calculate price correlation matrix for given symbols."""
        import math

        histories = {}
        for symbol in symbols:
            data = await self.get_price_history(symbol, hours)
            if data:
                histories[symbol] = [d["price"] for d in data if "price" in d]

        # Align by index (truncate to shortest)
        if not histories:
            return {"symbols": symbols, "matrix": []}

        min_len = min(len(v) for v in histories.values()) if histories else 0
        if min_len < 2:
            return {"symbols": symbols, "matrix": [[1.0] * len(symbols) for _ in symbols]}

        aligned = {k: v[-min_len:] for k, v in histories.items()}

        def _correlation(x: List[float], y: List[float]) -> float:
            n = len(x)
            if n == 0:
                return 0.0
            mean_x = sum(x) / n
            mean_y = sum(y) / n
            num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
            den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
            den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
            if den_x == 0 or den_y == 0:
                return 0.0
            return num / (den_x * den_y)

        matrix = []
        for s1 in symbols:
            row = []
            for s2 in symbols:
                if s1 == s2:
                    row.append(1.0)
                elif s1 in aligned and s2 in aligned:
                    row.append(round(_correlation(aligned[s1], aligned[s2]), 4))
                else:
                    row.append(0.0)
            matrix.append(row)

        return {"symbols": symbols, "matrix": matrix}


class SentimentRepository(BaseRepository):
    """Repository for sentiment analysis results."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES["sentiment_analysis"])

    async def get_by_news_id(self, news_id: str) -> Optional[Dict[str, Any]]:
        """Get sentiment analysis for a news article."""
        return await self.find_one({"news_id": news_id})

    async def get_recent(
        self, hours: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent sentiment analyses."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={"created_at": {"$gte": since}},
            sort=[("created_at", -1)],
            limit=limit,
        )

    async def get_by_sentiment(
        self, sentiment: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get analyses with specific sentiment."""
        return await self.find_many(
            filter={"sentiment": sentiment},
            sort=[("confidence", -1)],
            limit=limit,
        )

    async def get_high_confidence(
        self, threshold: float = 0.75, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get high confidence sentiment analyses."""
        return await self.find_many(
            filter={"confidence": {"$gte": threshold}},
            sort=[("confidence", -1)],
            limit=limit,
        )

    async def get_sentiment_distribution(
        self, hours: int = 24
    ) -> Dict[str, int]:
        """Get sentiment distribution for a time period."""
        since = datetime.utcnow() - timedelta(hours=hours)
        collection = await self._get_collection()
        pipeline = [
            {"$match": {"created_at": {"$gte": since}}},
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}},
        ]
        results = await collection.aggregate(pipeline).to_list(length=10)
        return {r["_id"]: r["count"] for r in results}

    async def get_sentiment_trend(
        self, hours: int = 24, interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get sentiment trend data bucketed by time intervals."""
        since = datetime.utcnow() - timedelta(hours=hours)
        collection = await self._get_collection()
        pipeline = [
            {"$match": {"created_at": {"$gte": since}}},
            {
                "$group": {
                    "_id": {
                        "$toDate": {
                            "$subtract": [
                                {"$toLong": "$created_at"},
                                {"$mod": [{"$toLong": "$created_at"}, interval_minutes * 60 * 1000]},
                            ]
                        }
                    },
                    "bullish_count": {
                        "$sum": {"$cond": [{"$eq": ["$sentiment", "bullish"]}, 1, 0]}
                    },
                    "bearish_count": {
                        "$sum": {"$cond": [{"$eq": ["$sentiment", "bearish"]}, 1, 0]}
                    },
                    "neutral_count": {
                        "$sum": {"$cond": [{"$eq": ["$sentiment", "neutral"]}, 1, 0]}
                    },
                    "avg_confidence": {"$avg": "$confidence"},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        results = await collection.aggregate(pipeline).to_list(length=200)
        return [
            {
                "timestamp": r["_id"].isoformat(),
                "bullish_count": r["bullish_count"],
                "bearish_count": r["bearish_count"],
                "neutral_count": r["neutral_count"],
                "avg_confidence": round(r["avg_confidence"], 3),
            }
            for r in results
        ]

    async def get_source_credibility(self) -> List[Dict[str, Any]]:
        """Get news source credibility scores based on article count and sentiment confidence."""
        collection = await self._get_collection()
        pipeline = [
            {
                "$group": {
                    "_id": "$source",
                    "article_count": {"$sum": 1},
                }
            },
            {"$sort": {"article_count": -1}},
        ]
        source_counts = await collection.aggregate(pipeline).to_list(length=50)

        results = []
        for sc in source_counts:
            source = sc["_id"]
            # Get average confidence for this source's sentiment analyses
            news_repo = NewsRepository()
            source_news = await news_repo.find_many(
                filter={"source": source}, limit=50
            )
            news_ids = [str(n["_id"]) for n in source_news]

            if news_ids:
                avg_pipeline = [
                    {"$match": {"news_id": {"$in": news_ids}}},
                    {"$group": {"_id": None, "avg_confidence": {"$avg": "$confidence"}}},
                ]
                avg_result = await collection.aggregate(avg_pipeline).to_list(length=1)
                avg_confidence = avg_result[0]["avg_confidence"] if avg_result else 0.5
            else:
                avg_confidence = 0.5

            credibility = min(1.0, (sc["article_count"] / 50) * 0.4 + avg_confidence * 0.6)
            results.append({
                "source": source,
                "article_count": sc["article_count"],
                "avg_confidence": round(avg_confidence, 3),
                "credibility_score": round(credibility, 3),
            })

        return sorted(results, key=lambda x: x["credibility_score"], reverse=True)


class ImpactRepository(BaseRepository):
    """Repository for impact analysis results."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES["impact_analysis"])

    async def get_by_news_id(self, news_id: str) -> Optional[Dict[str, Any]]:
        """Get impact analysis for a news article."""
        return await self.find_one({"news_id": news_id})

    async def get_high_impact(
        self, hours: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get high impact analyses."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={
                "risk_level": "high",
                "created_at": {"$gte": since},
            },
            sort=[("created_at", -1)],
            limit=limit,
        )

    async def get_by_symbol(
        self, symbol: str, hours: int = 24, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get impact analyses for a specific symbol."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={
                "affected_assets.symbol": symbol,
                "created_at": {"$gte": since},
            },
            sort=[("created_at", -1)],
            limit=limit,
        )

    async def get_impact_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get impact analysis summary."""
        since = datetime.utcnow() - timedelta(hours=hours)
        collection = await self._get_collection()
        pipeline = [
            {"$match": {"created_at": {"$gte": since}}},
            {
                "$group": {
                    "_id": "$risk_level",
                    "count": {"$sum": 1},
                    "avg_impact_score": {"$avg": "$impact_score"},
                }
            },
        ]
        results = await collection.aggregate(pipeline).to_list(length=10)
        return {r["_id"]: {"count": r["count"], "avg_score": r["avg_impact_score"]} for r in results}


class AlertRepository(BaseRepository):
    """Repository for alert history."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES["alerts"])

    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={"sent_at": {"$gte": since}},
            sort=[("sent_at", -1)],
            limit=limit,
        )

    async def get_by_channel(
        self, channel: str, hours: int = 24, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get alerts by channel."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.find_many(
            filter={"channel": channel, "sent_at": {"$gte": since}},
            sort=[("sent_at", -1)],
            limit=limit,
        )

    async def get_pending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending alerts to send."""
        return await self.find_many(
            filter={"status": "pending"},
            sort=[("created_at", 1)],
            limit=limit,
        )

    async def mark_sent(self, alert_id: str) -> bool:
        """Mark alert as sent."""
        return await self.update_one(
            filter={"_id": ObjectId(alert_id)},
            update={
                "$set": {
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                }
            },
        )

    async def mark_failed(self, alert_id: str, error: str) -> bool:
        """Mark alert as failed."""
        return await self.update_one(
            filter={"_id": ObjectId(alert_id)},
            update={
                "$set": {
                    "status": "failed",
                    "error": error,
                },
                "$inc": {"retry_count": 1},
            },
        )

    async def was_alerted_recently(
        self, impact_id: str, cooldown_minutes: int = 30
    ) -> bool:
        """Check if we already alerted for this impact recently."""
        since = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
        return await self.exists(
            {
                "impact_id": impact_id,
                "status": "sent",
                "sent_at": {"$gte": since},
            }
        )

    async def get_alert_count_last_hour(self) -> int:
        """Get count of alerts sent in the last hour."""
        since = datetime.utcnow() - timedelta(hours=1)
        return await self.count({"status": "sent", "sent_at": {"$gte": since}})


class WatchlistRepository(BaseRepository):
    """Repository for user watchlists."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES["watchlist"])

    async def get_user_watchlist(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Get user's watchlist."""
        return await self.find_many(
            filter={"user_id": user_id},
            sort=[("created_at", -1)],
        )

    async def add_to_watchlist(
        self,
        symbol: str,
        asset_type: str,
        user_id: str = "default",
        alert_on: List[str] = None,
    ) -> Optional[str]:
        """Add symbol to watchlist."""
        if alert_on is None:
            alert_on = ["high", "medium"]

        # Check if already exists
        existing = await self.find_one(
            {"user_id": user_id, "symbol": symbol}
        )
        if existing:
            return str(existing["_id"])

        return await self.insert_one(
            {
                "user_id": user_id,
                "symbol": symbol,
                "asset_type": asset_type,
                "alert_on": alert_on,
                "created_at": datetime.utcnow(),
            }
        )

    async def remove_from_watchlist(
        self, symbol: str, user_id: str = "default"
    ) -> bool:
        """Remove symbol from watchlist."""
        return await self.delete_one({"user_id": user_id, "symbol": symbol})

    async def get_watchlist_symbols(self, user_id: str = "default") -> List[str]:
        """Get all symbols in user's watchlist."""
        watchlist = await self.get_user_watchlist(user_id)
        return [item["symbol"] for item in watchlist]

    async def get_all_symbols(self) -> List[str]:
        """Get all unique symbols across all watchlists."""
        collection = await self._get_collection()
        return await collection.distinct("symbol")


class JobRunRepository(BaseRepository):
    """Repository for job run logs."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES.get("job_runs", "job_runs"))

    async def log_run(
        self,
        agent_name: str,
        status: str,
        items_processed: int = 0,
        items_new: int = 0,
        error: Optional[str] = None,
    ) -> str:
        """Log an agent job run."""
        return await self.insert_one(
            {
                "agent_name": agent_name,
                "status": status,
                "items_processed": items_processed,
                "items_new": items_new,
                "error": error,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
            }
        )

    async def get_recent_runs(
        self, agent_name: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent job runs."""
        filter_query = {}
        if agent_name:
            filter_query["agent_name"] = agent_name
        return await self.find_many(
            filter=filter_query,
            sort=[("started_at", -1)],
            limit=limit,
        )


class UserRepository(BaseRepository):
    """Repository for user authentication."""

    def __init__(self):
        super().__init__(COLLECTION_NAMES.get("users", "users"))

    async def create_user(
        self, username: str, email: str, hashed_password: str
    ) -> Optional[str]:
        """Create a new user."""
        existing = await self.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing:
            return None
        return await self.insert_one(
            {
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "is_active": True,
                "role": "user",
                "created_at": datetime.utcnow(),
            }
        )

    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        return await self.find_one({"username": username})

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        return await self.find_one({"email": email})