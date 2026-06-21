"""CoinGecko API client for crypto market data."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger
from src.agents.base import BaseAgent, AgentResult
from config.settings import settings
from config.constants import (
    COINGECKO_BASE_URL,
    COINGECKO_ENDPOINTS,
    CRYPTO_SYMBOL_TO_COINGECKO,
)


class CoinGeckoClient(BaseAgent):
    """CoinGecko API client for crypto market data."""

    def __init__(self):
        super().__init__("CoinGeckoClient", rate_limit_rpm=50)
        self.api_key = settings.coingecko_api_key

    @property
    def headers(self) -> Dict[str, str]:
        if self.api_key:
            return {"x-cg-demo-api-key": self.api_key}
        return {}

    def _url(self, endpoint: str) -> str:
        return f"{COINGECKO_BASE_URL}{endpoint}"

    def symbol_to_coingecko_id(self, symbol: str) -> Optional[str]:
        """Convert symbol to CoinGecko ID."""
        return CRYPTO_SYMBOL_TO_COINGECKO.get(symbol.upper())

    async def get_simple_price(
        self, ids: List[str], vs_currencies: List[str] = None
    ) -> Dict[str, Any]:
        """Get simple price for one or more coins."""
        if vs_currencies is None:
            vs_currencies = ["usd"]

        try:
            data = await self.get(
                url=self._url(COINGECKO_ENDPOINTS["simple_price"]),
                headers=self.headers,
                params={
                    "ids": ",".join(ids),
                    "vs_currencies": ",".join(vs_currencies),
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                },
            )
            return data
        except Exception as e:
            logger.error(f"CoinGecko simple price failed: {e}")
            return {}

    async def get_coins_markets(
        self,
        vs_currency: str = "usd",
        order: str = "market_cap_desc",
        per_page: int = 100,
        page: int = 1,
        sparkline: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get coins market data."""
        try:
            data = await self.get(
                url=self._url(COINGECKO_ENDPOINTS["coins_markets"]),
                headers=self.headers,
                params={
                    "vs_currency": vs_currency,
                    "order": order,
                    "per_page": min(per_page, 250),
                    "page": page,
                    "sparkline": sparkline,
                    "price_change_percentage": "1h,24h,7d",
                },
            )
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"CoinGecko markets failed: {e}")
            return []

    async def get_coin_details(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed coin information."""
        try:
            data = await self.get(
                url=self._url(f"{COINGECKO_ENDPOINTS['coin_details']}/{coin_id}"),
                headers=self.headers,
                params={
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false",
                },
            )
            return data if data else None
        except Exception as e:
            logger.error(f"CoinGecko coin details failed for {coin_id}: {e}")
            return None

    async def get_market_chart(
        self, coin_id: str, vs_currency: str = "usd", days: int = 1
    ) -> Optional[Dict[str, Any]]:
        """Get market chart data."""
        try:
            data = await self.get(
                url=self._url(f"{COINGECKO_ENDPOINTS['coin_market_chart'].format(id=coin_id)}"),
                headers=self.headers,
                params={
                    "vs_currency": vs_currency,
                    "days": days,
                },
            )
            return data if data else None
        except Exception as e:
            logger.error(f"CoinGecko chart failed for {coin_id}: {e}")
            return None

    async def get_trending(self) -> List[Dict[str, Any]]:
        """Get trending coins."""
        try:
            data = await self.get(
                url=self._url(COINGECKO_ENDPOINTS["trending"]),
                headers=self.headers,
            )
            coins = data.get("coins", [])
            return coins
        except Exception as e:
            logger.error(f"CoinGecko trending failed: {e}")
            return []

    async def get_global_data(self) -> Optional[Dict[str, Any]]:
        """Get global crypto market data."""
        try:
            data = await self.get(
                url=self._url(COINGECKO_ENDPOINTS["global"]),
                headers=self.headers,
            )
            return data.get("data", {})
        except Exception as e:
            logger.error(f"CoinGecko global data failed: {e}")
            return None

    async def get_crypto_prices(
        self, symbols: List[str], vs_currency: str = "usd"
    ) -> List[Dict[str, Any]]:
        """Get prices for crypto symbols."""
        coin_ids = []
        symbol_to_id = {}
        for symbol in symbols:
            coin_id = self.symbol_to_coingecko_id(symbol)
            if coin_id:
                coin_ids.append(coin_id)
                symbol_to_id[coin_id] = symbol.upper()

        if not coin_ids:
            return []

        prices = await self.get_simple_price(
            ids=coin_ids,
            vs_currencies=[vs_currency],
        )

        results = []
        for coin_id, price_data in prices.items():
            symbol = symbol_to_id.get(coin_id, coin_id)
            results.append({
                "symbol": symbol,
                "price": price_data.get(vs_currency, 0),
                "market_cap": price_data.get(f"{vs_currency}_market_cap", 0),
                "volume_24h": price_data.get(f"{vs_currency}_24h_vol", 0),
                "change_24h": price_data.get(f"{vs_currency}_24h_change", 0),
                "coin_id": coin_id,
                "timestamp": datetime.utcnow(),
                "source": "coingecko",
            })

        return results

    async def execute(self) -> AgentResult:
        """Execute client test."""
        try:
            global_data = await self.get_global_data()
            return AgentResult(
                agent_name=self.name,
                status="success",
                metadata={
                    "api": "coingecko",
                    "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0)
                    if global_data
                    else 0,
                },
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                errors=[str(e)],
            )