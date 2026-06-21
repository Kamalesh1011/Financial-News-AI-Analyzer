"""Alert message formatter for different channels."""
from typing import Any, Dict, List
from config.constants import RISK_EMOJI, SENTIMENT_EMOJI, DIRECTION_EMOJI, RISK_COLOR


class AlertFormatter:
    """Formatter for alert messages."""

    @staticmethod
    def format_telegram_alert(
        title: str,
        risk_emoji: str,
        risk_level: str,
        sentiment: str,
        confidence: float,
        affected_assets: str,
        reasoning: str,
        source_url: str,
        timestamp: str,
    ) -> str:
        """Format a Telegram alert message."""
        sentiment_emoji = SENTIMENT_EMOJI.get(sentiment, "➡️")

        message = f"""
🚨 *{risk_emoji} HIGH IMPACT ALERT*

📰 *{title}*

💰 *Sentiment:* {sentiment_emoji} {sentiment} ({confidence:.0%})
⚡ *Risk Level:* {risk_emoji} {risk_level}

📈 *Affected Assets:*
{affected_assets}

📝 *AI Analysis:*
{reasoning}

🔗 [Read More]({source_url})
⏱️ {timestamp}
"""
        return message.strip()

    @staticmethod
    def format_email_alert(
        title: str,
        risk_emoji: str,
        risk_level: str,
        sentiment: str,
        confidence: float,
        affected_assets: List[Dict[str, Any]],
        reasoning: str,
        source_url: str,
        timestamp: str,
    ) -> str:
        """Format an email alert message."""
        sentiment_emoji = SENTIMENT_EMOJI.get(sentiment, "➡️")
        risk_color = RISK_COLOR.get(risk_level, "#999")

        assets_rows = ""
        for asset in affected_assets[:10]:
            direction = asset.get("direction", "neutral")
            direction_emoji = DIRECTION_EMOJI.get(direction, "➡️")
            confidence_pct = f"{asset.get('confidence', 0):.0%}"
            assets_rows += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{asset.get('symbol', '')}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{direction_emoji} {direction}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{confidence_pct}</td>
            </tr>
            """

        html = f"""
        <h2 style="color: {risk_color};">{risk_emoji} HIGH IMPACT ALERT</h2>
        <h3>{title}</h3>
        <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Sentiment</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{sentiment_emoji} {sentiment} ({confidence:.0%})</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Risk Level</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{risk_emoji} {risk_level}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Timestamp</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{timestamp}</td>
            </tr>
        </table>
        <h4>Affected Assets</h4>
        <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
            <thead>
                <tr>
                    <th style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;">Symbol</th>
                    <th style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;">Direction</th>
                    <th style="padding: 8px; border: 1px solid #ddd; background: #f5f5f5;">Confidence</th>
                </tr>
            </thead>
            <tbody>
                {assets_rows}
            </tbody>
        </table>
        <h4>AI Analysis</h4>
        <p style="background: #f9f9f9; padding: 15px; border-radius: 5px;">{reasoning}</p>
        <p><a href="{source_url}" style="color: #667eea;">Read Full Article</a></p>
        <hr style="margin: 20px 0;">
        <p style="color: #888; font-size: 12px;">Financial News AI Analyzer</p>
        """

        return html

    @staticmethod
    def format_summary_card(
        title: str,
        sentiment: str,
        confidence: float,
        risk_level: str,
        affected_count: int,
    ) -> str:
        """Format a summary card for dashboard."""
        sentiment_emoji = SENTIMENT_EMOJI.get(sentiment, "➡️")
        risk_emoji = RISK_EMOJI.get(risk_level, "⚪")

        return f"""
**{title[:60]}{'...' if len(title) > 60 else ''}**

{sentiment_emoji} {sentiment.title()} ({confidence:.0%}) | {risk_emoji} {risk_level.title()}
📈 {affected_count} assets affected
"""