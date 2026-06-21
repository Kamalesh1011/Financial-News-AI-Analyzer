"""Alert Engine Agent - Sends alerts for high-impact events."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger

from src.agents.base import BaseAgent, AgentResult
from src.db.repositories import (
    ImpactRepository,
    AlertRepository,
    WatchlistRepository,
)
from src.alerts.telegram_bot import TelegramBot
from src.alerts.email_sender import EmailSender
from src.alerts.formatter import AlertFormatter
from config.settings import settings
from config.constants import RISK_EMOJI, SENTIMENT_EMOJI


class AlertEngineAgent(BaseAgent):
    """Agent that evaluates and sends alerts for high-impact events."""

    def __init__(self):
        super().__init__("AlertEngineAgent", rate_limit_rpm=20)
        self.impact_repo = ImpactRepository()
        self.alert_repo = AlertRepository()
        self.watchlist_repo = WatchlistRepository()
        self.telegram: TelegramBot = None
        self.email: EmailSender = None

    async def initialize(self) -> None:
        """Initialize the agent."""
        await super().initialize()
        self.telegram = TelegramBot()
        self.email = EmailSender()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.telegram:
            await self.telegram.cleanup()
        if self.email:
            await self.email.cleanup()
        await super().cleanup()

    async def get_high_impact_events(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get high impact events that need alerts."""
        # Get high impact analyses
        high_impact = await self.impact_repo.get_high_impact(hours=hours, limit=20)

        # Filter for watchlist symbols
        watchlist_symbols = set(await self.watchlist_repo.get_watchlist_symbols())

        filtered = []
        for impact in high_impact:
            affected_assets = impact.get("affected_assets", [])
            for asset in affected_assets:
                if asset.get("symbol") in watchlist_symbols:
                    filtered.append(impact)
                    break

        return filtered

    async def should_alert(self, impact: Dict[str, Any]) -> bool:
        """Determine if we should send an alert for this impact."""
        risk_level = impact.get("risk_level", "low")
        news_id = str(impact.get("news_id", ""))

        # Check cooldown
        if await self.alert_repo.was_alerted_recently(
            news_id, cooldown_minutes=settings.alert_cooldown_minutes
        ):
            return False

        # Check rate limit
        alert_count = await self.alert_repo.get_alert_count_last_hour()
        if alert_count >= settings.max_alerts_per_hour:
            logger.warning(f"Alert rate limit reached: {alert_count}/{settings.max_alerts_per_hour}")
            return False

        return True

    async def create_alert(self, impact: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert document."""
        news = impact.get("news", {})
        sentiment = impact.get("sentiment", {})

        title = news.get("title", "Unknown Event")
        risk_level = impact.get("risk_level", "medium")
        risk_emoji = RISK_EMOJI.get(risk_level, "⚪")

        affected_assets = impact.get("affected_assets", [])
        affected_text = "\n".join([
            f"  {SENTIMENT_EMOJI.get(a.get('direction'), '➡️')} **{a.get('symbol')}** ({a.get('direction', 'neutral')}) - {a.get('confidence', 0):.0%}"
            for a in affected_assets[:5]
        ])

        # Create markdown message
        markdown = AlertFormatter.format_telegram_alert(
            title=title,
            risk_emoji=risk_emoji,
            risk_level=risk_level,
            sentiment=sentiment.get("sentiment", "neutral"),
            confidence=sentiment.get("confidence", 0.5),
            affected_assets=affected_text,
            reasoning=impact.get("reasoning", ""),
            source_url=news.get("url", ""),
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        )

        # Create HTML message for email
        html = AlertFormatter.format_email_alert(
            title=title,
            risk_emoji=risk_emoji,
            risk_level=risk_level,
            sentiment=sentiment.get("sentiment", "neutral"),
            confidence=sentiment.get("confidence", 0.5),
            affected_assets=affected_assets,
            reasoning=impact.get("reasoning", ""),
            source_url=news.get("url", ""),
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        )

        return {
            "impact_id": str(impact.get("_id", "")),
            "subject": f"{risk_emoji} {risk_level.upper()}: {title[:80]}",
            "body_markdown": markdown,
            "body_html": html,
            "risk_level": risk_level,
            "affected_assets": affected_assets,
        }

    async def send_alerts(self, alert_data: Dict[str, Any]) -> Dict[str, bool]:
        """Send alerts to all configured channels."""
        results = {}

        # Send to Telegram
        if settings.telegram_enabled:
            try:
                telegram_alert = await self.alert_repo.insert_one({
                    "impact_id": alert_data["impact_id"],
                    "channel": "telegram",
                    "recipient": settings.telegram_chat_id,
                    "subject": alert_data["subject"],
                    "body_markdown": alert_data["body_markdown"],
                    "status": "pending",
                    "created_at": datetime.utcnow(),
                })

                success = await self.telegram.send_message(
                    alert_data["body_markdown"],
                    parse_mode="Markdown",
                )

                await self.alert_repo.update_one(
                    {"_id": telegram_alert},
                    {"$set": {"status": "sent" if success else "failed", "sent_at": datetime.utcnow()}}
                )

                results["telegram"] = success
            except Exception as e:
                logger.error(f"Telegram alert failed: {e}")
                results["telegram"] = False

        # Send to Email
        if settings.email_enabled:
            try:
                email_alert = await self.alert_repo.insert_one({
                    "impact_id": alert_data["impact_id"],
                    "channel": "email",
                    "recipient": settings.alert_email_to,
                    "subject": alert_data["subject"],
                    "body_html": alert_data["body_html"],
                    "status": "pending",
                    "created_at": datetime.utcnow(),
                })

                success = await self.email.send_email(
                    to_email=settings.alert_email_to,
                    subject=alert_data["subject"],
                    html_body=alert_data["body_html"],
                )

                await self.alert_repo.update_one(
                    {"_id": email_alert},
                    {"$set": {"status": "sent" if success else "failed", "sent_at": datetime.utcnow()}}
                )

                results["email"] = success
            except Exception as e:
                logger.error(f"Email alert failed: {e}")
                results["email"] = False

        return results

    async def execute(self) -> AgentResult:
        """Execute the alert engine."""
        # Get high impact events
        high_impact = await self.get_high_impact_events(hours=1)
        if not high_impact:
            return AgentResult(
                agent_name=self.name,
                status="success",
                items_processed=0,
                metadata={"message": "No high impact events"},
            )

        logger.info(f"Found {len(high_impact)} high impact events")

        alerts_sent = 0
        alerts_failed = 0
        errors = []

        for impact in high_impact:
            try:
                # Check if we should alert
                if not await self.should_alert(impact):
                    continue

                # Create alert
                alert_data = await self.create_alert(impact)

                # Send alerts
                send_results = await self.send_alerts(alert_data)

                if any(send_results.values()):
                    alerts_sent += 1
                else:
                    alerts_failed += 1

            except Exception as e:
                alerts_failed += 1
                errors.append(str(e))
                logger.error(f"Alert processing failed: {e}")

        return AgentResult(
            agent_name=self.name,
            status="success" if not errors else "partial",
            items_processed=len(high_impact),
            items_new=alerts_sent,
            errors=errors,
            metadata={
                "events_evaluated": len(high_impact),
                "alerts_sent": alerts_sent,
                "alerts_failed": alerts_failed,
            },
        )