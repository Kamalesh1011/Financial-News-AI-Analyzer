"""News Collector Agent - Fetches news from Finnhub and NewsAPI."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Set
from loguru import logger

from src.agents.base import BaseAgent, AgentResult
from src.api.finnhub_client import FinnhubClient
from src.api.newsapi_client import NewsAPIClient
from src.db.repositories import NewsRepository
from src.utils.deduplication import ContentDeduplicator
from config.settings import settings


class NewsCollectorAgent(BaseAgent):
    """Agent that collects news from multiple sources."""

    def __init__(self):
        super().__init__("NewsCollectorAgent", rate_limit_rpm=120)
        self.news_repo = NewsRepository()
        self.deduplicator = ContentDeduplicator()
        self.finnhub = FinnhubClient()
        self.newsapi = NewsAPIClient()

    async def initialize(self) -> None:
        """Initialize the agent."""
        await super().initialize()
        await self.finnhub.initialize()
        await self.newsapi.initialize()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.finnhub.cleanup()
        await self.newsapi.cleanup()
        await super().cleanup()

    async def collect_finnhub_news(self) -> List[Dict[str, Any]]:
        """Collect news from Finnhub."""
        articles = []

        # Get general market news
        general_news = await self.finnhub.get_general_news(category="general")
        for article in general_news:
            normalized = self._normalize_finnhub_article(article)
            if normalized:
                articles.append(normalized)

        # Get company news for watched symbols
        from src.db.repositories import WatchlistRepository
        watchlist_repo = WatchlistRepository()
        symbols = await watchlist_repo.get_watchlist_symbols()

        for symbol in symbols[:5]:
            try:
                company_news = await self.finnhub.get_company_news(symbol)
                for article in company_news:
                    normalized = self._normalize_finnhub_article(article, primary_ticker=symbol)
                    if normalized:
                        articles.append(normalized)
            except Exception as e:
                logger.warning(f"Failed to get company news for {symbol}: {e}")
            await asyncio.sleep(0.1)

        return articles

    def _normalize_finnhub_article(
        self, article: Dict[str, Any], primary_ticker: str = None
    ) -> Dict[str, Any]:
        """Normalize Finnhub article to standard format."""
        try:
            published_at = datetime.fromtimestamp(article.get("datetime", 0))
            tickers = []
            if primary_ticker:
                tickers.append(primary_ticker)

            return {
                "source": "finnhub",
                "source_name": article.get("source", "Finnhub"),
                "external_id": str(article.get("id", "")),
                "title": article.get("headline", ""),
                "summary": article.get("summary", ""),
                "url": article.get("url", ""),
                "published_at": published_at,
                "tickers": tickers,
                "raw_data": article,
            }
        except Exception as e:
            logger.debug(f"Failed to normalize Finnhub article: {e}")
            return None

    async def collect_newsapi_news(self) -> List[Dict[str, Any]]:
        """Collect news from NewsAPI."""
        if not settings.newsapi_enabled:
            logger.info("NewsAPI not configured, skipping")
            return []

        articles = await self.newsapi.get_financial_news(page_size=100)
        normalized = []
        for article in articles:
            normalized_article = self.newsapi.normalize_article(article)
            if normalized_article.get("title") and normalized_article.get("url"):
                normalized.append(normalized_article)
        return normalized

    def extract_tickers_from_text(self, text: str) -> List[str]:
        """Extract mentioned tickers from article text."""
        tickers = set()
        text_upper = text.upper()

        # Common stock tickers
        known_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
            "SPY", "QQQ", "DIA", "IWM", "VOO", "VTI",
            "BTC", "ETH", "SOL", "ADA", "XRP",
            "JPM", "V", "MA", "WMT", "PG", "KO", "PEP",
            "DIS", "NFLX", "CRM", "ORCL", "INTC", "AMD",
        ]

        for ticker in known_tickers:
            if f" {ticker} " in f" {text_upper} " or f"${ticker}" in text_upper:
                tickers.add(ticker)

        # Check for company names
        company_to_ticker = {
            "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL",
            "AMAZON": "AMZN", "NVIDIA": "NVDA", "META": "META",
            "TESLA": "TSLA", "NETFLIX": "NFLX", "SALESFORCE": "CRM",
            "BITCOIN": "BTC", "ETHEREUM": "ETH", "SOLANA": "SOL",
        }

        for company, ticker in company_to_ticker.items():
            if company in text_upper:
                tickers.add(ticker)

        return list(tickers)

    async def store_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Store new articles in database."""
        new_count = 0

        for article in articles:
            url = article.get("url", "")
            title = article.get("title", "")
            source = article.get("source", "")

            if not url or not title:
                continue

            # Check deduplication
            if self.deduplicator.is_duplicate(title, source):
                continue

            # Check database
            if await self.news_repo.exists_by_url(url):
                self.deduplicator.mark_seen(title, source)
                continue

            # Extract tickers
            text = f"{title} {article.get('summary', '')}"
            tickers = self.extract_tickers_from_text(text)
            if article.get("tickers"):
                tickers.extend(article["tickers"])
            article["tickers"] = list(set(tickers))

            # Store
            try:
                article["created_at"] = datetime.utcnow()
                await self.news_repo.insert_one(article)
                self.deduplicator.mark_seen(title, source)
                new_count += 1
            except Exception as e:
                logger.error(f"Failed to store article: {e}")

        return new_count

    async def execute(self) -> AgentResult:
        """Execute the news collection."""
        all_articles = []
        errors = []
        finnhub_count = 0
        newsapi_count = 0

        # Collect from Finnhub
        try:
            finnhub_articles = await self.collect_finnhub_news()
            all_articles.extend(finnhub_articles)
            finnhub_count = len(finnhub_articles)
            logger.info(f"Finnhub: collected {finnhub_count} articles")
        except Exception as e:
            errors.append(f"Finnhub error: {e}")
            logger.error(f"Finnhub collection failed: {e}")

        # Collect from NewsAPI
        try:
            newsapi_articles = await self.collect_newsapi_news()
            all_articles.extend(newsapi_articles)
            newsapi_count = len(newsapi_articles)
            logger.info(f"NewsAPI: collected {newsapi_count} articles")
        except Exception as e:
            errors.append(f"NewsAPI error: {e}")
            logger.error(f"NewsAPI collection failed: {e}")

        # Store articles
        new_count = await self.store_articles(all_articles)

        status = "success" if not errors else "partial" if new_count > 0 else "failed"

        return AgentResult(
            agent_name=self.name,
            status=status,
            items_processed=len(all_articles),
            items_new=new_count,
            errors=errors,
            metadata={
                "finnhub_count": finnhub_count,
                "newsapi_count": newsapi_count,
                "deduplicator_stats": self.deduplicator.get_stats(),
            },
        )