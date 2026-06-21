"""Binance API client for crypto market data."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from loguru import logger
from src.agents.base import BaseAgent, AgentResult
from config.settings import settings
from config.constants import BINANCE_BASE_URL, BINANCE_ENDPOINTS, CRYPTO_SYMBOL_TO_BINANCE


class BinanceClient(BaseAgent):
    """Binance API client for crypto market data."""

    def __init__(self):
        super().__init__("BinanceClient", rate_limit_rpm=1200)

    def _url(self, endpoint: str) -> str:
        return f"{BINANCE_BASE_URL}{endpoint}"

    def symbol_to_binance(self, symbol: str) -> str:
        """Convert symbol to Binance trading pair."""
        upper = symbol.upper()
        if upper in CRYPTO_SYMBOL_TO_BINANCE:
            return CRYPTO_SYMBOL_TO_BINANCE[upper]
        if upper.endswith("USDT"):
            return upper
        return f"{upper}USDT"

    async def get_ticker_24h(self, symbol: Optional[str] = None) -> Any:
        """Get 24h ticker price change statistics."""
        params = {}
        if symbol:
            params["symbol"] = self.symbol_to_binance(symbol)

        try:
            data = await self.get(
                url=self._url(BINANCE_ENDPOINTS["ticker_24h"]),
                params=params,
            )
            return data
        except Exception as e:
            logger.error(f"Binance ticker failed: {e}")
            return {} if symbol else []

    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get kline/candlestick data."""
        binance_symbol = self.symbol_to_binance(symbol)
        params = {
            "symbol": binance_symbol,
            "interval": interval,
            "limit": min(limit, 1000),
        }

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        try:
            data = await self.get(
                url=self._url(BINANCE_ENDPOINTS["klines"]),
                params=params,
            )

            klines = []
            for k in data:
                klines.append({
                    "open_time": datetime.fromtimestamp(k[0] / 1000),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": datetime.fromtimestamp(k[6] / 1000),
                    "quote_volume": float(k[7]),
                    "trades": int(k[8]),
                    "symbol": binance_symbol,
                })

            return klines
        except Exception as e:
            logger.error(f"Binance klines failed for {symbol}: {e}")
            return []

    async def get_depth(self, symbol: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get order book depth."""
        binance_symbol = self.symbol_to_binance(symbol)
        try:
            data = await self.get(
                url=self._url(BINANCE_ENDPOINTS["depth"]),
                params={"symbol": binance_symbol, "limit": min(limit, 5000)},
            )

            return {
                "symbol": binance_symbol,
                "bids": [[float(p), float(q)] for p, q in data.get("bids", [])],
                "asks": [[float(p), float(q)] for p, q in data.get("asks", [])],
                "last_update": data.get("lastUpdateId", 0),
            }
        except Exception as e:
            logger.error(f"Binance depth failed for {symbol}: {e}")
            return None

    async def get_avg_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current average price."""
        binance_symbol = self.symbol_to_binance(symbol)
        try:
            data = await self.get(
                url=self._url(BINANCE_ENDPOINTS["avg_price"]),
                params={"symbol": binance_symbol},
            )

            return {
                "symbol": binance_symbol,
                "price": float(data.get("price", 0)),
                "weighted_avg": float(data.get("weightedAvgPrice", 0)),
                "count": int(data.get("count", 0)),
            }
        except Exception as e:
            logger.error(f"Binance avg price failed for {symbol}: {e}")
            return None

    async def get_crypto_prices(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get prices for multiple crypto symbols."""
        all_tickers = await self.get_ticker_24h()
        if not all_tickers:
            return []

        symbol_map = {}
        for symbol in symbols:
            binance_symbol = self.symbol_to_binance(symbol)
            symbol_map[binance_symbol] = symbol.upper()

        results = []
        for ticker in all_tickers:
            symbol = ticker.get("symbol", "")
            if symbol in symbol_map:
                original_symbol = symbol_map[symbol]
                results.append({
                    "symbol": original_symbol,
                    "price": float(ticker.get("lastPrice", 0)),
                    "change_24h": float(ticker.get("priceChange", 0)),
                    "change_pct_24h": float(ticker.get("priceChangePercent", 0)),
                    "high_24h": float(ticker.get("highPrice", 0)),
                    "low_24h": float(ticker.get("lowPrice", 0)),
                    "volume": float(ticker.get("volume", 0)),
                    "quote_volume": float(ticker.get("quoteVolume", 0)),
                    "trades": int(ticker.get("count", 0)),
                    "timestamp": datetime.utcnow(),
                    "source": "binance",
                })

        return results

    async def get_recent_trades(
        self, symbol: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent trades."""
        binance_symbol = self.symbol_to_binance(symbol)
        try:
            data = await self.get(
                url=self._url(BINANCE_ENDPOINTS["trades"]),
                params={"symbol": binance_symbol, "limit": min(limit, 1000)},
            )

            trades = []
            for trade in data:
                trades.append({
                    "price": float(trade.get("price", 0)),
                    "quantity": float(trade.get("qty", 0)),
                    "time": datetime.fromtimestamp(trade.get("time", 0) / 1000),
                    "is_buyer": trade.get("isBuyerMaker", False),
                })

            return trades
        except Exception as e:
            logger.error(f"Binance trades failed for {symbol}: {e}")
            return []

    async def execute(self) -> AgentResult:
        """Execute client test."""
        try:
            btc_price = await self.get_avg_price("BTC")
            return AgentResult(
                agent_name=self.name,
                status="success",
                metadata={
                    "api": "binance",
                    "btc_price": btc_price.get("price", 0) if btc_price else 0,
                },
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                errors=[str(e)],
            )