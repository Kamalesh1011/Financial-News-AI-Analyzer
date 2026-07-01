"""Impact Mapper Agent - Maps news to affected assets and risk levels."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger

from src.agents.base import BaseAgent, AgentResult
from src.ai.openrouter_client import OpenRouterClient
from src.ai.nim_client import NIMClient
from src.ai.prompts import PromptTemplates
from src.db.repositories import (
    NewsRepository,
    SentimentRepository,
    ImpactRepository,
    MarketDataRepository,
)
from config.settings import settings
from config.constants import RISK_LEVELS, SENTIMENT_LABELS


class ImpactMapperAgent(BaseAgent):
    """Agent that maps news to affected assets and calculates impact."""

    def __init__(self):
        super().__init__("ImpactMapperAgent", rate_limit_rpm=30)
        self.news_repo = NewsRepository()
        self.sentiment_repo = SentimentRepository()
        self.impact_repo = ImpactRepository()
        self.market_repo = MarketDataRepository()
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

    async def get_articles_with_sentiment(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get articles that have sentiment but no impact analysis."""
        pipeline = [
            {
                "$lookup": {
                    "from": "sentiment_analysis",
                    "let": {"article_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$news_id", {"$toString": "$$article_id"}]
                                }
                            }
                        }
                    ],
                    "as": "sentiment",
                }
            },
            {"$unwind": {"path": "$sentiment", "preserveNullAndEmptyArrays": False}},
            {
                "$lookup": {
                    "from": "impact_analysis",
                    "let": {"article_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$news_id", {"$toString": "$$article_id"}]
                                }
                            }
                        }
                    ],
                    "as": "impact",
                }
            },
            {"$match": {"impact": {"$size": 0}}},
            {"$sort": {"created_at": -1}},
            {"$limit": limit},
        ]

        collection = await self.news_repo._get_collection()
        return await collection.aggregate(pipeline).to_list(length=limit)

    def calculate_risk_level(
        self,
        sentiment_confidence: float,
        impact_score: float,
        article_source: str,
    ) -> str:
        """Calculate risk level based on multiple factors."""
        # Base score from sentiment confidence
        base_score = sentiment_confidence

        # Amplify by impact magnitude
        impact_magnitude = abs(impact_score)
        adjusted_score = base_score * (1 + impact_magnitude * 0.3)

        # Source credibility boost
        credible_sources = ["reuters", "bloomberg", "wsj", "cnbc", "financial times"]
        if any(source in article_source.lower() for source in credible_sources):
            adjusted_score *= 1.1

        # Determine risk level
        if adjusted_score >= settings.high_risk_confidence_threshold:
            return "high"
        elif adjusted_score >= settings.medium_risk_confidence_threshold:
            return "medium"
        return "low"

    async def analyze_impact(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact for a single article."""
        sentiment = article.get("sentiment", {})

        messages = PromptTemplates.format_impact_prompt(
            article=article,
            sentiment=sentiment,
        )

        try:
            if settings.openrouter_enabled:
                response = await self.openrouter.complete_json(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000,
                )
            elif settings.nim_enabled:
                response = await self.nim.complete_json(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000,
                )
            else:
                # Rule-based fallback
                response = self.rule_based_impact(article, sentiment)

            # Validate and normalize
            response = self.validate_impact(response)

            # Calculate risk level
            risk_level = self.calculate_risk_level(
                sentiment_confidence=sentiment.get("confidence", 0.5),
                impact_score=response.get("impact_score", 0),
                article_source=article.get("source", ""),
            )
            response["risk_level"] = risk_level

            return response

        except Exception as e:
            logger.error(f"Impact analysis failed: {e}")
            return self.rule_based_impact(article, sentiment)

    def rule_based_impact(
        self, article: Dict[str, Any], sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rule-based impact analysis fallback."""
        sentiment_label = sentiment.get("sentiment", "neutral")
        confidence = sentiment.get("confidence", 0.5)
        tickers = article.get("tickers", [])

        affected_assets = []
        for ticker in tickers:
            asset_type = "stock"
            if ticker in ["BTC", "ETH", "SOL", "ADA", "XRP"]:
                asset_type = "crypto"
            elif ticker in ["EURUSD=X", "GBPUSD=X"]:
                asset_type = "forex"
            elif ticker in ["GLD", "SLV"]:
                asset_type = "commodity"
            elif ticker in ["SPY", "QQQ", "DIA", "IWM"]:
                asset_type = "etf"

            affected_assets.append({
                "symbol": ticker,
                "direction": sentiment_label,
                "confidence": confidence * 0.8,
                "asset_type": asset_type,
                "reasoning": f"Based on news sentiment: {sentiment_label}",
            })

        impact_score = 0.0
        if sentiment_label == "bullish":
            impact_score = confidence * 0.5
        elif sentiment_label == "bearish":
            impact_score = -confidence * 0.5

        return {
            "impact_score": impact_score,
            "risk_level": "medium",
            "reasoning": f"Rule-based analysis: {sentiment_label} sentiment",
            "affected_assets": affected_assets,
        }

    def validate_impact(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize impact result."""
        # Validate impact score
        impact_score = result.get("impact_score", 0)
        if not isinstance(impact_score, (int, float)):
            impact_score = 0.0
        impact_score = max(-1.0, min(1.0, float(impact_score)))

        # Validate risk level
        risk_level = result.get("risk_level", "medium")
        if risk_level not in RISK_LEVELS:
            risk_level = "medium"

        # Validate affected assets
        affected_assets = result.get("affected_assets", [])
        validated_assets = []
        for asset in affected_assets:
            direction = asset.get("direction", "neutral")
            if direction not in SENTIMENT_LABELS:
                direction = "neutral"

            confidence = asset.get("confidence", 0.5)
            if not isinstance(confidence, (int, float)):
                confidence = 0.5
            confidence = max(0.0, min(1.0, float(confidence)))

            validated_assets.append({
                "symbol": asset.get("symbol", ""),
                "direction": direction,
                "confidence": confidence,
                "asset_type": asset.get("asset_type", "stock"),
                "reasoning": asset.get("reasoning", ""),
            })

        return {
            "impact_score": impact_score,
            "risk_level": risk_level,
            "reasoning": result.get("reasoning", ""),
            "affected_assets": validated_assets,
        }

    async def store_results(
        self,
        articles: List[Dict[str, Any]],
        results: List[Dict[str, Any]],
    ) -> int:
        """Store impact analysis results."""
        stored_count = 0

        for article, result in zip(articles, results):
            try:
                news_id = str(article["_id"])
                sentiment = article.get("sentiment", {})
                sentiment_id = str(sentiment.get("_id", ""))

                # Check if already exists
                existing = await self.impact_repo.get_by_news_id(news_id)
                if existing:
                    continue

                document = {
                    "news_id": news_id,
                    "sentiment_id": sentiment_id,
                    "affected_assets": result["affected_assets"],
                    "risk_level": result["risk_level"],
                    "reasoning": result["reasoning"],
                    "impact_score": result["impact_score"],
                    "created_at": datetime.utcnow(),
                }

                await self.impact_repo.insert_one(document)
                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store impact result: {e}")

        return stored_count

    async def execute(self) -> AgentResult:
        """Execute the impact analysis."""
        # Get articles with sentiment but no impact
        articles = await self.get_articles_with_sentiment(limit=15)
        if not articles:
            return AgentResult(
                agent_name=self.name,
                status="success",
                items_processed=0,
                metadata={"message": "No articles to analyze"},
            )

        logger.info(f"Analyzing impact for {len(articles)} articles")

        # Analyze impact
        results = []
        for article in articles:
            result = await self.analyze_impact(article)
            results.append(result)
            await asyncio.sleep(0.1)  # Rate limiting

        # Store results
        stored_count = await self.store_results(articles, results)

        # Calculate stats
        risk_levels = [r.get("risk_level", "medium") for r in results]
        total_assets = sum(len(r.get("affected_assets", [])) for r in results)

        return AgentResult(
            agent_name=self.name,
            status="success",
            items_processed=len(articles),
            items_new=stored_count,
            metadata={
                "articles_analyzed": len(articles),
                "risk_distribution": {
                    "high": risk_levels.count("high"),
                    "medium": risk_levels.count("medium"),
                    "low": risk_levels.count("low"),
                },
                "total_assets_affected": total_assets,
            },
        )