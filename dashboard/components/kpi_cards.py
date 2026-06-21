"""KPI cards component with 3D glassmorphism effect."""
import streamlit as st
from typing import Optional


def render_kpi_row(
    news_count: int = 0,
    bullish_pct: float = 0.0,
    high_impact: int = 0,
    alerts_sent: int = 0,
    news_delta: int = 0,
    sentiment_delta: float = 0.0,
    impact_delta: int = 0,
    alert_delta: int = 0,
) -> None:
    """Render the KPI cards row with 3D glass effect."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_type = "positive" if news_delta >= 0 else "negative"
        delta_text = f"+{news_delta}" if news_delta >= 0 else str(news_delta)
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid #60A5FA;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.5rem;">📰</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">News Today</span>
                </div>
                <div class="kpi-number">{news_count}</div>
                <div class="kpi-delta {delta_type}" style="margin-top: 8px;">
                    {'↑' if news_delta >= 0 else '↓'} {delta_text} vs yesterday
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        sentiment_color = "#16A34A" if bullish_pct >= 50 else "#DC2626" if bullish_pct < 40 else "#F59E0B"
        sentiment_label = "Bullish" if bullish_pct >= 50 else "Bearish" if bullish_pct < 40 else "Neutral"
        sentiment_emoji = "📈" if bullish_pct >= 50 else "📉" if bullish_pct < 40 else "➡️"
        delta_type = "positive" if sentiment_delta >= 0 else "negative"
        delta_text = f"+{sentiment_delta:.1f}%" if sentiment_delta >= 0 else f"{sentiment_delta:.1f}%"

        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {sentiment_color};">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.5rem;">📊</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">Market Sentiment</span>
                </div>
                <div class="kpi-number" style="font-size: 2rem;">{bullish_pct:.0f}%</div>
                <div style="margin-top: 8px;">
                    <span class="sentiment-badge {sentiment_label.lower()}">{sentiment_emoji} {sentiment_label}</span>
                </div>
                <div class="kpi-delta {delta_type}" style="margin-top: 8px;">
                    {'↑' if sentiment_delta >= 0 else '↓'} {delta_text} from 24h
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        risk_color = "#DC2626" if high_impact >= 5 else "#F59E0B" if high_impact >= 2 else "#16A34A"
        risk_label = "High" if high_impact >= 5 else "Medium" if high_impact >= 2 else "Low"
        risk_emoji = "🔴" if high_impact >= 5 else "🟡" if high_impact >= 2 else "🟢"
        delta_type = "negative" if impact_delta > 0 else "positive" if impact_delta < 0 else "neutral"
        delta_text = f"+{impact_delta}" if impact_delta >= 0 else str(impact_delta)

        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {risk_color};">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.5rem;">⚡</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">High Impact Events</span>
                </div>
                <div class="kpi-number" style="font-size: 2rem;">{high_impact}</div>
                <div style="margin-top: 8px;">
                    <span class="risk-badge {risk_label.lower()}">{risk_emoji} {risk_label} Risk</span>
                </div>
                <div class="kpi-delta {delta_type}" style="margin-top: 8px;">
                    {'↑' if impact_delta >= 0 else '↓'} {delta_text} from peak
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        alert_color = "#60A5FA" if alerts_sent > 0 else "#94A3B8"
        delta_type = "positive" if alert_delta >= 0 else "negative"
        delta_text = f"+{alert_delta}" if alert_delta >= 0 else str(alert_delta)

        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid {alert_color};">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.5rem;">🔔</span>
                    <span style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">Alerts Sent</span>
                </div>
                <div class="kpi-number" style="font-size: 2rem;">{alerts_sent}</div>
                <div style="margin-top: 8px;">
                    <span class="sentiment-badge bullish">✅ Active</span>
                </div>
                <div class="kpi-delta {delta_type}" style="margin-top: 8px;">
                    {'↑' if alert_delta >= 0 else '↓'} {delta_text} this hour
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )