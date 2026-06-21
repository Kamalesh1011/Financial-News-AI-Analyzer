"""NewsAPI client for financial news."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from loguru import logger
from src.agents.base import BaseAgent, AgentResult
from config.settings import settings
from config.constants import NEWSAPI_BASE_URL, NEWSAPI_ENDPOINTS, NEWS_KEYWORDS


class NewsAPIClient(BaseAgent):
    """NewsAPI client for financial news."""

    def __init__(self):
        super().__init__("NewsAPIClient", rate_limit_rpm=100)
        self.api_key = settings.newsapi_api_key

    @property
    def headers(self) -> Dict[str, str]:
        return {}

    def _url(self, endpoint: str) -> str:
        return f"{NEWSAPI_BASE_URL}{endpoint}"

    async def get_everything(
        self,
        query: Optional[str] = None,
        sources: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 100,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get everything endpoint."""
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        if not query:
            query = " OR ".join(NEWS_KEYWORDS[:10])

        if not from_date:
            from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not to_date:
            to_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "apiKey": self.api_key,
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),
            "page": page,
            "from": from_date,
            "to": to_date,
        }

        if sources:
            params["sources"] = ",".join(sources[:20])
        if domains:
            params["domains"] = ",".join(domains[:20])

        try:
            data = await self.get(
                url=self._url(NEWSAPI_ENDPOINTS["everything"]),
                params=params,
            )
            articles = data.get("articles", [])
            total = data.get("totalResults", 0)
            logger.info(f"NewsAPI: Got {len(articles)} articles (total: {total})")
            return articles
        except Exception as e:
            logger.error(f"NewsAPI everything failed: {e}")
            return []

    async def get_top_headlines(
        self,
        country: str = "us",
        category: str = "business",
        query: Optional[str] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get top headlines."""
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        params = {
            "apiKey": self.api_key,
            "country": country,
            "category": category,
            "pageSize": min(page_size, 100),
        }

        if query:
            params["q"] = query

        try:
            data = await self.get(
                url=self._url(NEWSAPI_ENDPOINTS["top_headlines"]),
                params=params,
            )
            articles = data.get("articles", [])
            logger.info(f"NewsAPI headlines: Got {len(articles)} articles")
            return articles
        except Exception as e:
            logger.error(f"NewsAPI headlines failed: {e}")
            return []

    async def get_financial_news(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get financial news from multiple approaches."""
        all_articles = []

        # Approach 1: Top headlines with business category
        headlines = await self.get_top_headlines(
            category="business",
            page_size=page_size,
        )
        all_articles.extend(headlines)

        # Approach 2: Everything with financial keywords
        if len(all_articles) < page_size:
            financial_keywords = [
                "stock market", "fed", "inflation", "earnings",
                "bitcoin", "crypto", "interest rate", "recession"
            ]
            for keyword in financial_keywords[:3]:
                articles = await self.get_everything(
                    query=keyword,
                    page_size=30,
                    sort_by="publishedAt",
                )
                all_articles.extend(articles)

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

        logger.info(f"NewsAPI total unique articles: {len(unique_articles)}")
        return unique_articles[:page_size]

    def normalize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize NewsAPI article to standard format."""
        source = article.get("source", {})
        published_str = article.get("publishedAt", "")
        published_at = None
        if published_str:
            try:
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            except Exception:
                published_at = datetime.utcnow()

        return {
            "source": "newsapi",
            "external_id": article.get("url", ""),
            "title": article.get("title", "") or "",
            "summary": article.get("description", "") or "",
            "url": article.get("url", ""),
            "published_at": published_at or datetime.utcnow(),
            "author": article.get("author", ""),
            "source_name": source.get("name", ""),
            "image_url": article.get("urlToImage", ""),
            "content": article.get("content", ""),
        }

    async def execute(self) -> AgentResult:
        """Execute client test."""
        if not self.api_key:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                errors=["NewsAPI key not configured"],
            )

        try:
            articles = await self.get_top_headlines(page_size=5)
            return AgentResult(
                agent_name=self.name,
                status="success",
                items_processed=len(articles),
                metadata={"api": "newsapi", "tested": True},
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                errors=[str(e)],
            )