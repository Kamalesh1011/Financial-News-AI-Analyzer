"""Database package for MongoDB async client."""
from .mongodb import MongoDB, get_mongodb
from .models import (
    RawNewsDocument,
    MarketDataDocument,
    SentimentAnalysisDocument,
    ImpactAnalysisDocument,
    AlertDocument,
    WatchlistDocument,
)
from .repositories import (
    NewsRepository,
    MarketDataRepository,
    SentimentRepository,
    ImpactRepository,
    AlertRepository,
    WatchlistRepository,
)

__all__ = [
    "MongoDB",
    "get_mongodb",
    "RawNewsDocument",
    "MarketDataDocument",
    "SentimentAnalysisDocument",
    "ImpactAnalysisDocument",
    "AlertDocument",
    "WatchlistDocument",
    "NewsRepository",
    "MarketDataRepository",
    "SentimentRepository",
    "ImpactRepository",
    "AlertRepository",
    "WatchlistRepository",
]