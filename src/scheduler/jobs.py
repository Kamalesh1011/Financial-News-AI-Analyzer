"""Agent scheduler for running jobs on intervals."""
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config.settings import settings
from src.db.mongodb import MongoDB
from src.agents.news_collector import NewsCollectorAgent
from src.agents.market_collector import MarketDataCollectorAgent
from src.agents.sentiment_analyzer import SentimentAnalyzerAgent
from src.agents.impact_mapper import ImpactMapperAgent
from src.agents.alert_engine import AlertEngineAgent
from src.agents.base import AgentResult


class AgentScheduler:
    """Scheduler for running agent jobs."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False

    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        db = MongoDB()
        await db.connect()

        self.scheduler.add_job(
            self.run_news_collector,
            IntervalTrigger(minutes=settings.news_fetch_interval_minutes),
            id="news_collector",
            name="News Collector",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.run_market_collector,
            IntervalTrigger(minutes=settings.market_fetch_interval_minutes),
            id="market_collector",
            name="Market Data Collector",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.run_sentiment_analyzer,
            IntervalTrigger(minutes=settings.news_fetch_interval_minutes),
            id="sentiment_analyzer",
            name="Sentiment Analyzer",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.run_impact_mapper,
            IntervalTrigger(minutes=settings.news_fetch_interval_minutes),
            id="impact_mapper",
            name="Impact Mapper",
            replace_existing=True,
        )

        self.scheduler.add_job(
            self.run_alert_engine,
            IntervalTrigger(minutes=1),
            id="alert_engine",
            name="Alert Engine",
            replace_existing=True,
        )

        self.scheduler.start()
        self._running = True
        logger.info("Agent scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            logger.info("Agent scheduler stopped")

    async def run_news_collector(self) -> AgentResult:
        """Run news collector agent."""
        agent = NewsCollectorAgent()
        return await agent.run()

    async def run_market_collector(self) -> AgentResult:
        """Run market data collector agent."""
        agent = MarketDataCollectorAgent()
        return await agent.run()

    async def run_sentiment_analyzer(self) -> AgentResult:
        """Run sentiment analyzer agent."""
        agent = SentimentAnalyzerAgent()
        return await agent.run()

    async def run_impact_mapper(self) -> AgentResult:
        """Run impact mapper agent."""
        agent = ImpactMapperAgent()
        return await agent.run()

    async def run_alert_engine(self) -> AgentResult:
        """Run alert engine agent."""
        agent = AlertEngineAgent()
        return await agent.run()

    async def run_all(self) -> Dict[str, AgentResult]:
        """Run all agents sequentially."""
        results = {}

        logger.info("Running all agents...")

        results["news"] = await self.run_news_collector()
        logger.info(f"News collector: {results['news'].status}")

        results["market"] = await self.run_market_collector()
        logger.info(f"Market collector: {results['market'].status}")

        results["sentiment"] = await self.run_sentiment_analyzer()
        logger.info(f"Sentiment analyzer: {results['sentiment'].status}")

        results["impact"] = await self.run_impact_mapper()
        logger.info(f"Impact mapper: {results['impact'].status}")

        results["alerts"] = await self.run_alert_engine()
        logger.info(f"Alert engine: {results['alerts'].status}")

        return results

    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs