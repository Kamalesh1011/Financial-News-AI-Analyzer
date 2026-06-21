"""Finnhub API client for market data and news."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from loguru import logger
from src.agents.base import BaseAgent, AgentResult
from config.settings import settings
from config.constants import FINNHUB_BASE_URL, FINNHUB_ENDPOINTS


class FinnhubClient(BaseAgent):
    """Finnhub API client for market data and news."""

    def __init__(self):
        super().__init__("FinnhubClient", rate_limit_rpm=60)
        self.api_key = settings.finnhub_api_key

    @property
    def headers(self) -> Dict[str, str]:
        return {"X-Finnhub-Token": self.api_key}

    def _url(self, endpoint: str) -> str:
        return f"{FINNHUB_BASE_URL}{endpoint}"

    async def get_general_news(self, category: str = "general") -> List[Dict[str, Any]]:
        """Get general market news."""
        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["market_news"]),
                headers=self.headers,
                params={"category": category, "minId": 0},
            )
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Finnhub general news failed: {e}")
            return []

    async def get_company_news(
        self, symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get company-specific news."""
        if not from_date:
            from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.utcnow().strftime("%Y-%m-%d")

        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["company_news"]),
                headers=self.headers,
                params={"symbol": symbol, "from": from_date, "to": to_date},
            )
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Finnhub company news failed for {symbol}: {e}")
            return []

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol."""
        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["quote"]),
                headers=self.headers,
                params={"symbol": symbol},
            )
            if data and data.get("c") is not None:
                return {
                    "symbol": symbol,
                    "price": data["c"],
                    "change": data.get("d", 0),
                    "change_pct": data.get("dp", 0),
                    "open": data.get("o", 0),
                    "high": data.get("h", 0),
                    "low": data.get("l", 0),
                    "previous_close": data.get("pc", 0),
                    "timestamp": datetime.utcnow(),
                    "source": "finnhub",
                }
            return None
        except Exception as e:
            logger.error(f"Finnhub quote failed for {symbol}: {e}")
            return None

    async def get_stock_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile."""
        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["stock_profile"]),
                headers=self.headers,
                params={"symbol": symbol},
            )
            return data if data else None
        except Exception as e:
            logger.error(f"Finnhub stock profile failed for {symbol}: {e}")
            return None

    async def get_peers(self, symbol: str) -> List[str]:
        """Get peer symbols."""
        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["peers"]),
                headers=self.headers,
                params={"symbol": symbol},
            )
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Finnhub peers failed for {symbol}: {e}")
            return []

    async def get_forex_rates(self, base: str = "USD") -> Optional[Dict[str, Any]]:
        """Get forex rates."""
        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["forex"]),
                headers=self.headers,
                params={"base": base},
            )
            return data
        except Exception as e:
            logger.error(f"Finnhub forex rates failed: {e}")
            return None

    async def get_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get news sentiment for a symbol."""
        try:
            data = await self.get(
                url=self._url(FINNHUB_ENDPOINTS["sentiment"]),
                headers=self.headers,
                params={"symbol": symbol},
            )
            if data and "sentiment" in data:
                return {
                    "symbol": symbol,
                    "buzz": data.get("buzz", {}),
                    "sentiment": data["sentiment"],
                    "companyNewsScore": data.get("companyNewsScore", 0),
                }
            return None
        except Exception as e:
            logger.error(f"Finnhub sentiment failed for {symbol}: {e}")
            return None

    async def execute(self) -> AgentResult:
        """Execute client initialization check."""
        try:
            await self.get_quote("AAPL")
            return AgentResult(
                agent_name=self.name,
                status="success",
                metadata={"api": "finnhub", "checked": "quote"},
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                errors=[str(e)],
            )