"""Alert history component with glassmorphism styling."""
import streamlit as st
from typing import Any, Dict, List


def render_alert_history(alerts: List[Dict[str, Any]]) -> None:
    """Render the alert history with glass styling."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h2 style="margin: 0; color: var(--text-primary);">🔔 Alert History</h2>
            <span style="color: var(--text-tertiary); font-size: 0.85rem;">Recent notifications</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not alerts:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🔔</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">No alerts sent yet</h3>
                <p style="color: var(--text-secondary);">The Alert Engine will notify you of important events.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for alert in alerts[:10]:
        alert_type = alert.get("type", "info")
        title = alert.get("title", "Alert")
        message = alert.get("message", "")[:150]
        timestamp = alert.get("timestamp", "")
        assets = alert.get("assets", [])
        channel = alert.get("channel", "unknown")

        # Type-based styling
        type_emoji = {
            "high_impact": "🚨",
            "sentiment_shift": "📊",
            "price_move": "📈",
            "info": "ℹ️",
        }.get(alert_type, "🔔")

        type_color = {
            "high_impact": "#DC2626",
            "sentiment_shift": "#F59E0B",
            "price_move": "#16A34A",
            "info": "#60A5FA",
        }.get(alert_type, "#94A3B8")

        channel_emoji = "📨" if channel == "email" else "📱" if channel == "telegram" else "🔔"

        # Format timestamp
        if timestamp:
            if isinstance(timestamp, str):
                time_str = timestamp[:19]
            else:
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = "Unknown"

        # Build asset chips
        asset_chips = ""
        for asset in assets[:4]:
            asset_chips += f"""
                <span class="asset-chip neutral" style="font-size: 0.75rem; padding: 4px 10px;">
                    {asset}
                </span>
            """

        st.markdown(
            f"""
            <div class="news-card neutral" style="margin-bottom: 12px; border-left: 4px solid {type_color};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.3rem;">{type_emoji}</span>
                        <div>
                            <div style="font-weight: 600; font-size: 1rem; color: var(--text-primary);">
                                {title}
                            </div>
                            <div style="color: var(--text-tertiary); font-size: 0.8rem; margin-top: 2px;">
                                {time_str} • {channel_emoji} {channel.title()}
                            </div>
                        </div>
                    </div>
                </div>
                {"<div style='color: var(--text-secondary); font-size: 0.85rem; margin: 8px 0 12px; line-height: 1.5;'>" + message + "</div>" if message else ""}
                {"<div style='display: flex; align-items: center; gap: 8px; flex-wrap: wrap;'>" + asset_chips + "</div>" if asset_chips else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )