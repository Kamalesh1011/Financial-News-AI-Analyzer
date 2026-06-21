"""Dashboard components package."""
from .news_feed import render_news_feed
from .market_panel import render_market_panel
from .sentiment_chart import render_sentiment_chart
from .impact_view import render_impact_view
from .alert_history import render_alert_history
from .watchlist_manager import render_watchlist_manager

__all__ = [
    "render_news_feed",
    "render_market_panel",
    "render_sentiment_chart",
    "render_impact_view",
    "render_alert_history",
    "render_watchlist_manager",
]