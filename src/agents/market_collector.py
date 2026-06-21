"""Market Data Collector Agent - Fetches prices from multiple sources."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger

from src.agents.base import BaseAgent, AgentResult
from src.api.finnhub_client import FinnhubClient
from src.api.coingecko_client import CoinGeckoClient
from src.api.binance_client import BinanceClient
from src.db.repositories import MarketDataRepository, NewsRepository
from config.settings import settings
from config.constants import CRYPTO_SYMBOL_TO_COINGECKO


class MarketDataCollectorAgent(BaseAgent):
    """Agent that collects market data from multiple sources."""

    def __init__(self):
        super().__init__("MarketDataCollectorAgent", rate_limit_rpm=200)
        self.market_repo = MarketDataRepository()
        self.news_repo = NewsRepository()
        self.finnhub = FinnhubClient()
        self.coingecko = CoinGeckoClient()
        self.binance = BinanceClient()

    async def initialize(self) -> None:
        """Initialize the agent."""
        await super().initialize()
        await self.finnhub.initialize()
        await self.coingecko.initialize()
        await self.binance.initialize()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.finnhub.cleanup()
        await self.coingecko.cleanup()
        await self.binance.cleanup()
        await super().cleanup()

    async def get_symbols_to_track(self) -> List[Dict[str, str]]:
        """Get list of symbols to track."""
        symbols = []

        # Get from watchlist
        from src.db.repositories import WatchlistRepository
        watchlist_repo = WatchlistRepository()
        watchlist = await watchlist_repo.get_user_watchlist()

        for item in watchlist:
            symbols.append({
                "symbol": item["symbol"],
                "asset_type": item.get("asset_type", "stock"),
            })

        # Get from recent news tickers
        recent_news = await self.news_repo.get_recent(hours=6, limit=50)
        seen_symbols = {s["symbol"] for s in symbols}
        for news in recent_news:
            for ticker in news.get("tickers", []):
                if ticker not in seen_symbols:
                    asset_type = "crypto" if ticker in CRYPTO_SYMBOL_TO_COINGECKO else "stock"
                    symbols.append({"symbol": ticker, "asset_type": asset_type})
                    seen_symbols.add(ticker)

        return symbols

    async def collect_stock_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Collect stock/forex data from Finnhub."""
        results = []

        for symbol in symbols:
            try:
                quote = await self.finnhub.get_quote(symbol)
                if quote:
                    results.append(quote)
            except Exception as e:
                logger.error(f"Failed to get quote for {symbol}: {e}")
            await asyncio.sleep(0.1)  # Rate limiting

        return results

    async def collect_crypto_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Collect crypto data from CoinGecko and Binance."""
        results = []

        # CoinGecko for market cap and detailed data
        try:
            coingecko_data = await self.coingecko.get_crypto_prices(symbols)
            results.extend(coingecko_data)
        except Exception as e:
            logger.error(f"CoinGecko collection failed: {e}")

        # Binance for price and volume
        try:
            binance_data = await self.binance.get_crypto_prices(symbols)
            # Merge with existing data or add new
            existing_symbols = {r["symbol"]: r for r in results}
            for item in binance_data:
                if item["symbol"] in existing_symbols:
                    existing = existing_symbols[item["symbol"]]
                    existing.update({
                        "price": item["price"],
                        "change_24h": item.get("change_24h"),
                        "change_pct_24h": item.get("change_pct_24h"),
                        "high_24h": item.get("high_24h"),
                        "low_24h": item.get("low_24h"),
                        "volume": item.get("volume"),
                    })
                else:
                    results.append(item)
        except Exception as e:
            logger.error(f"Binance collection failed: {e}")

        return results

    async def store_market_data(self, data_list: List[Dict[str, Any]]) -> int:
        """Store market data in database."""
        stored_count = 0

        for data in data_list:
            try:
                document = {
                    "symbol": data["symbol"],
                    "price": data.get("price", 0),
                    "change_24h": data.get("change_24h"),
                    "change_pct_24h": data.get("change_pct_24h"),
                    "volume": data.get("volume"),
                    "market_cap": data.get("market_cap"),
                    "high_24h": data.get("high_24h"),
                    "low_24h": data.get("low_24h"),
                    "timestamp": data.get("timestamp", datetime.utcnow()),
                    "source": data.get("source", "unknown"),
                }

                await self.market_repo.insert_one(document)
                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store market data for {data.get('symbol')}: {e}")

        return stored_count

    async def execute(self) -> AgentResult:
        """Execute the market data collection."""
        symbols = await self.get_symbols_to_track()
        if not symbols:
            return AgentResult(
                agent_name=self.name,
                status="success",
                items_processed=0,
                metadata={"message": "No symbols to track"},
            )

        # Separate stocks and crypto
        stock_symbols = [s["symbol"] for s in symbols if s["asset_type"] in ("stock", "etf", "forex")]
        crypto_symbols = [s["symbol"] for s in symbols if s["asset_type"] == "crypto"]

        all_data = []
        errors = []

        # Collect stock data
        if stock_symbols:
            try:
                stock_data = await self.collect_stock_data(stock_symbols)
                all_data.extend(stock_data)
                logger.info(f"Collected data for {len(stock_data)} stocks")
            except Exception as e:
                errors.append(f"Stock collection error: {e}")

        # Collect crypto data
        if crypto_symbols:
            try:
                crypto_data = await self.collect_crypto_data(crypto_symbols)
                all_data.extend(crypto_data)
                logger.info(f"Collected data for {len(crypto_data)} crypto assets")
            except Exception as e:
                errors.append(f"Crypto collection error: {e}")

        # Store data
        stored_count = await self.store_market_data(all_data)

        status = "success" if not errors else "partial" if stored_count > 0 else "failed"

        return AgentResult(
            agent_name=self.name,
            status=status,
            items_processed=len(all_data),
            items_new=stored_count,
            errors=errors,
            metadata={
                "symbols_tracked": len(symbols),
                "stock_symbols": len(stock_symbols),
                "crypto_symbols": len(crypto_symbols),
            },
        )