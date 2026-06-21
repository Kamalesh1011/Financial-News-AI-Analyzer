"""Data fetching utilities for the dashboard."""
import os
import httpx
from typing import Any, Dict, List, Optional
from loguru import logger


def get_api_base() -> str:
    """Get the API base URL."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


async def fetch_news(hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch news articles from API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{get_api_base()}/api/news",
                params={"hours": hours, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("articles", [])
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return []


async def fetch_market_data(symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch market data from API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {}
            if symbols:
                params["symbols"] = symbols
            response = await client.get(
                f"{get_api_base()}/api/market",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")
        return []


async def fetch_sentiment_distribution(hours: int = 24) -> Dict[str, int]:
    """Fetch sentiment distribution from API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{get_api_base()}/api/sentiment/distribution",
                params={"hours": hours},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("distribution", {})
    except Exception as e:
        logger.error(f"Failed to fetch sentiment distribution: {e}")
        return {}


async def fetch_impact_analyses(hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch impact analyses from API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{get_api_base()}/api/impact",
                params={"hours": hours, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("analyses", [])
    except Exception as e:
        logger.error(f"Failed to fetch impact analyses: {e}")
        return []


async def fetch_alerts(hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch alert history from API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{get_api_base()}/api/alerts",
                params={"hours": hours, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("alerts", [])
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {e}")
        return []


async def fetch_watchlist() -> List[Dict[str, Any]]:
    """Fetch watchlist from API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{get_api_base()}/api/watchlist")
            response.raise_for_status()
            data = response.json()
            return data.get("watchlist", [])
    except Exception as e:
        logger.error(f"Failed to fetch watchlist: {e}")
        return []


async def add_to_watchlist(symbol: str, asset_type: str = "stock") -> bool:
    """Add an asset to the watchlist."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{get_api_base()}/api/watchlist",
                json={"symbol": symbol, "asset_type": asset_type},
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Failed to add to watchlist: {e}")
        return False


async def remove_from_watchlist(symbol: str) -> bool:
    """Remove an asset from the watchlist."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(
                f"{get_api_base()}/api/watchlist/{symbol}",
            )
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Failed to remove from watchlist: {e}")
        return False