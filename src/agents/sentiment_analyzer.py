"""Sentiment Analyzer Agent - Analyzes news sentiment using LLMs."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger

from src.agents.base import BaseAgent, AgentResult
from src.ai.openrouter_client import OpenRouterClient
from src.ai.nim_client import NIMClient
from src.ai.prompts import PromptTemplates
from src.db.repositories import NewsRepository, SentimentRepository
from config.settings import settings
from config.constants import SENTIMENT_LABELS


class SentimentAnalyzerAgent(BaseAgent):
    """Agent that analyzes sentiment of news articles using LLMs."""

    def __init__(self):
        super().__init__("SentimentAnalyzerAgent", rate_limit_rpm=30)
        self.news_repo = NewsRepository()
        self.sentiment_repo = SentimentRepository()
        self.openrouter: OpenRouterClient = None
        self.nim: NIMClient = None

    async def initialize(self) -> None:
        """Initialize the agent."""
        await super().initialize()
        self.openrouter = OpenRouterClient()
        self.nim = NIMClient()
        await self.openrouter.initialize()
        await self.nim.initialize()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.openrouter:
            await self.openrouter.cleanup()
        if self.nim:
            await self.nim.cleanup()
        await super().cleanup()

    async def get_unanalyzed_articles(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get articles that need sentiment analysis."""
        if limit is None:
            limit = settings.sentiment_batch_size
        return await self.news_repo.get_unprocessed(limit=limit)

    async def analyze_single(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of a single article."""
        messages = PromptTemplates.format_sentiment_prompt(article)

        try:
            # Try OpenRouter first
            if settings.openrouter_enabled:
                response = await self.openrouter.complete_json(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=500,
                )
                response["_model"] = settings.openrouter_model or "auto"
                response["_provider"] = "openrouter"
                return response

            # Fallback to NIM
            if settings.nim_enabled:
                response = await self.nim.complete_json(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=500,
                )
                response["_model"] = settings.nim_model
                response["_provider"] = "nim"
                return response

            # No LLM available - return neutral
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "key_events": [],
                "reasoning": "No LLM provider available",
                "_model": "none",
                "_provider": "none",
            }

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.3,
                "key_events": [],
                "reasoning": f"Analysis failed: {str(e)}",
                "_model": "fallback",
                "_provider": "error",
            }

    async def analyze_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment of a batch of articles."""
        if not articles:
            return []

        # Try batch analysis first
        messages = PromptTemplates.format_batch_sentiment_prompt(articles)

        try:
            if settings.openrouter_enabled:
                response = await self.openrouter.complete_json(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000,
                )
            elif settings.nim_enabled:
                response = await self.nim.complete_json(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000,
                )
            else:
                return [await self.analyze_single(a) for a in articles]

            # Parse batch response
            if isinstance(response, list) and len(response) == len(articles):
                for i, result in enumerate(response):
                    result["_model"] = settings.openrouter_model or "auto"
                    result["_provider"] = "openrouter"
                return response

        except Exception as e:
            logger.warning(f"Batch analysis failed, falling back to single: {e}")

        # Fallback to single analysis
        results = []
        for article in articles:
            result = await self.analyze_single(article)
            results.append(result)
            await asyncio.sleep(0.1)  # Rate limiting

        return results

    def validate_sentiment(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize sentiment result."""
        sentiment = result.get("sentiment", "neutral")
        if sentiment not in SENTIMENT_LABELS:
            sentiment = "neutral"

        confidence = result.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)):
            confidence = 0.5
        confidence = max(0.0, min(1.0, float(confidence)))

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "key_events": result.get("key_events", []) or [],
            "reasoning": result.get("reasoning", ""),
        }

    async def store_results(
        self,
        articles: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> int:
        """Store sentiment analysis results."""
        stored_count = 0

        for article, result in zip(articles, results):
            try:
                validated = self.validate_sentiment(result)
                news_id = str(article["_id"])

                # Check if already exists
                existing = await self.sentiment_repo.get_by_news_id(news_id)
                if existing:
                    continue

                document = {
                    "news_id": news_id,
                    "model": result.get("_model", "unknown"),
                    "sentiment": validated["sentiment"],
                    "confidence": validated["confidence"],
                    "key_events": validated["key_events"],
                    "reasoning": validated["reasoning"],
                    "tokens_used": 0,
                    "cost_usd": 0.0,
                    "created_at": datetime.utcnow(),
                }

                await self.sentiment_repo.insert_one(document)
                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store sentiment result: {e}")

        return stored_count

    async def execute(self) -> AgentResult:
        """Execute the sentiment analysis."""
        # Get unanalyzed articles
        articles = await self.get_unanalyzed_articles()
        if not articles:
            return AgentResult(
                agent_name=self.name,
                status="success",
                items_processed=0,
                metadata={"message": "No articles to analyze"},
            )

        logger.info(f"Analyzing sentiment for {len(articles)} articles")

        # Analyze sentiment
        results = await self.analyze_batch(articles)

        # Store results
        stored_count = await self.store_results(articles, results)

        # Calculate stats
        sentiments = [r.get("sentiment", "neutral") for r in results]
        avg_confidence = sum(r.get("confidence", 0) for r in results) / len(results) if results else 0

        return AgentResult(
            agent_name=self.name,
            status="success",
            items_processed=len(articles),
            items_new=stored_count,
            metadata={
                "articles_analyzed": len(articles),
                "sentiment_distribution": {
                    "bullish": sentiments.count("bullish"),
                    "bearish": sentiments.count("bearish"),
                    "neutral": sentiments.count("neutral"),
                },
                "avg_confidence": round(avg_confidence, 2),
            },
        )