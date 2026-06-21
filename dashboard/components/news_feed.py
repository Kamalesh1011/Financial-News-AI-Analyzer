"""News feed component with glassmorphism styling."""
import streamlit as st
from datetime import datetime
from typing import Any, Dict, List


def render_news_feed(articles: List[Dict[str, Any]]) -> None:
    """Render the news feed with glass cards."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h2 style="margin: 0; color: var(--text-primary);">📰 News Feed</h2>
            <span style="color: var(--text-tertiary); font-size: 0.85rem;">Auto-refreshes every 5 min</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not articles:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📰</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">No news articles yet</h3>
                <p style="color: var(--text-secondary);">The News Collector agent will fetch news automatically.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for i, article in enumerate(articles[:20]):
        title = article.get("title", "Untitled")
        url = article.get("url", "#")
        source = article.get("source", article.get("source_name", "Unknown"))
        published = article.get("published_at", "")
        summary = article.get("summary", "")[:200]
        tickers = article.get("tickers", [])

        # Get sentiment
        sentiment = article.get("sentiment", {})
        sentiment_label = sentiment.get("sentiment", "neutral") if sentiment else "neutral"
        confidence = sentiment.get("confidence", 0) if sentiment else 0

        # Format published time
        if published:
            if isinstance(published, str):
                time_str = published[:16]
            else:
                time_str = published.strftime("%Y-%m-%d %H:%M")
        else:
            time_str = "Unknown"

        # Build asset chips
        asset_chips = ""
        for ticker in tickers[:4]:
            asset_chips += f"""
                <span class="asset-chip" style="font-size: 0.75rem; padding: 4px 10px;">
                    {ticker}
                </span>
            """

        # Sentiment badge
        sentiment_emoji = "📈" if sentiment_label == "bullish" else "📉" if sentiment_label == "bearish" else "➡️"
        confidence_text = f" ({confidence:.0%})" if confidence > 0 else ""

        st.markdown(
            f"""
            <div class="news-card {sentiment_label}" style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <a href="{url}" target="_blank" style="text-decoration: none; color: var(--text-primary); font-weight: 600; font-size: 1.05rem; line-height: 1.4;">
                            {title}
                        </a>
                    </div>
                    <span class="sentiment-badge {sentiment_label}" style="margin-left: 12px; white-space: nowrap;">
                        {sentiment_emoji} {sentiment_label.title()}{confidence_text}
                    </span>
                </div>
                <div style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 12px;">
                    {source} • {time_str}
                </div>
                {"<div style='color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px; line-height: 1.5;'>{summary}...</div>" if summary else ""}
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    {asset_chips}
                    <a href="{url}" target="_blank" class="glass-btn" style="margin-left: auto; padding: 6px 12px; font-size: 0.8rem; text-decoration: none; color: var(--accent-blue);">
                        Read More →
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )