"""Configuration package for Financial News Analyzer."""
from .settings import settings
from .constants import (
    FINNHUB_BASE_URL,
    NEWSAPI_BASE_URL,
    COINGECKO_BASE_URL,
    BINANCE_BASE_URL,
    OPENROUTER_BASE_URL,
    NIM_BASE_URL,
    SENTIMENT_LABELS,
    RISK_LEVELS,
    ASSET_TYPES,
    DEFAULT_WATCHLIST,
    COLLECTION_NAMES,
    INDEXES,
)

__all__ = [
    "settings",
    "FINNHUB_BASE_URL",
    "NEWSAPI_BASE_URL",
    "COINGECKO_BASE_URL",
    "BINANCE_BASE_URL",
    "OPENROUTER_BASE_URL",
    "NIM_BASE_URL",
    "SENTIMENT_LABELS",
    "RISK_LEVELS",
    "ASSET_TYPES",
    "DEFAULT_WATCHLIST",
    "COLLECTION_NAMES",
    "INDEXES",
]