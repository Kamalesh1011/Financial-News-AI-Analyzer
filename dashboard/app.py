"""Main Streamlit dashboard application with premium glassmorphism UI."""
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

st.set_page_config(
    page_title="Financial News AI Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def run_async(coro):
    """Run async function in Streamlit."""
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coro)


def inject_global_styles():
    """Inject all global CSS styles."""
    # Load Google Fonts
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )

    # Load main CSS
    main_css = Path("dashboard/styles/main.css")
    if main_css.exists():
        st.markdown(f"<style>{main_css.read_text()}</style>", unsafe_allow_html=True)

    # Load theme CSS
    theme = st.session_state.get("theme", "dark")
    theme_css = Path(f"dashboard/styles/themes/{theme}.css")
    if theme_css.exists():
        st.markdown(f"<style>{theme_css.read_text()}</style>", unsafe_allow_html=True)


def render_header():
    """Render the main header."""
    st.markdown(
        """
        <div class="header-section">
            <div class="header-content">
                <div class="header-left">
                    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #60A5FA, #A78BFA, #F472B6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        📊 Financial News AI Analyzer
                    </h1>
                    <p style="margin: 8px 0 0; color: var(--text-secondary); font-size: 1.05rem;">
                        AI-powered sentiment analysis • Real-time market data • Smart alerts
                    </p>
                </div>
                <div class="header-right">
                    <div style="text-align: right;">
                        <div style="color: var(--text-tertiary); font-size: 0.8rem; margin-bottom: 4px;">
                            {date} • {time}
                        </div>
                        <div class="status-indicator online">
                            <span class="status-dot online"></span>
                            <span style="color: var(--text-primary);">Live</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """.format(
            date=datetime.now().strftime("%B %d, %Y"),
            time=datetime.now().strftime("%H:%M:%S"),
        ),
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    """Render the theme toggle in sidebar."""
    current_theme = st.session_state.get("theme", "dark")
    is_dark = current_theme == "dark"

    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])

        with col1:
            theme_name = "Obsidian Dark" if is_dark else "Arctic Light"
            theme_icon = "🌙" if is_dark else "☀️"
            st.markdown(f"**{theme_icon} {theme_name}**")

        with col2:
            if st.button(
                "☀️" if is_dark else "🌙",
                key="theme_toggle",
                help="Toggle theme",
            ):
                new_theme = "light" if is_dark else "dark"
                st.session_state.theme = new_theme
                st.rerun()


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        # Logo / Brand
        st.markdown(
            """
            <div style="text-align: center; padding: 20px 0;">
                <div style="font-size: 3rem; margin-bottom: 8px;">📊</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-primary);">FinNews AI</div>
                <div style="font-size: 0.8rem; color: var(--text-tertiary);">v1.0.0 • Free Tier</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # API Settings
        st.markdown(
            """
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px;">
                ⚙️ API Configuration
            </div>
            """,
            unsafe_allow_html=True,
        )

        api_base = st.text_input(
            "API Base URL",
            value=st.session_state.get("api_base", "http://localhost:8000"),
            help="FastAPI server URL",
            label_visibility="collapsed",
        )
        st.session_state["api_base"] = api_base

        st.markdown("---")

        # Quick Stats
        st.markdown(
            """
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px;">
                📈 System Status
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Status indicators
        for name, status in [
            ("MongoDB", "online"),
            ("OpenRouter API", "online"),
            ("Finnhub API", "online"),
            ("NewsAPI", "online"),
        ]:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0;">
                    <span style="color: var(--text-secondary); font-size: 0.85rem;">{name}</span>
                    <span class="status-dot {status}"></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Theme Toggle
        render_theme_toggle()

        # Auto-refresh
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        if auto_refresh:
            st.rerun()

        # Footer
        st.markdown(
            """
            <div style="text-align: center; padding: 20px 0; color: var(--text-tertiary); font-size: 0.75rem;">
                Built with Streamlit<br>
                Powered by OpenRouter + NIM
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    """Main dashboard application."""
    inject_global_styles()
    render_header()

    # Import components
    from dashboard.components.kpi_cards import render_kpi_row
    from dashboard.components.news_feed import render_news_feed
    from dashboard.components.market_panel import render_market_panel
    from dashboard.components.sentiment_chart import render_sentiment_chart
    from dashboard.components.impact_view import render_impact_view
    from dashboard.components.alert_history import render_alert_history
    from dashboard.components.watchlist_manager import render_watchlist_manager
    from dashboard.utils.data_fetch import (
        fetch_news,
        fetch_market_data,
        fetch_sentiment_distribution,
        fetch_impact_analyses,
        fetch_alerts,
        fetch_watchlist,
    )

    # Sidebar
    render_sidebar()

    # Main content
    with st.spinner("Loading data..."):
        news = run_async(fetch_news(hours=24, limit=30))
        market = run_async(fetch_market_data())
        sentiment = run_async(fetch_sentiment_distribution(hours=24))
        impacts = run_async(fetch_impact_analyses(hours=24, limit=20))
        alerts = run_async(fetch_alerts(hours=24, limit=30))

    # KPI Row
    bullish_pct = 0.0
    if sentiment:
        total = sum(s.get("count", 0) for s in sentiment)
        bullish_count = sum(s.get("count", 0) for s in sentiment if s.get("sentiment") == "bullish")
        bullish_pct = (bullish_count / total * 100) if total > 0 else 50.0

    high_impact = len([i for i in impacts if i.get("risk_level") == "high"])

    render_kpi_row(
        news_count=len(news),
        bullish_pct=bullish_pct,
        high_impact=high_impact,
        alerts_sent=len(alerts),
    )

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📰 News Feed",
        "💰 Market Data",
        "🎯 Impact Analysis",
        "🔔 Alerts",
        "📋 Watchlist",
    ])

    with tab1:
        render_news_feed(news)

    with tab2:
        render_market_panel(market)

    with tab3:
        col1, col2 = st.columns([1, 2])

        with col1:
            render_sentiment_chart(sentiment)

        with col2:
            render_impact_view(impacts)

    with tab4:
        render_alert_history(alerts)

    with tab5:
        with st.spinner("Loading watchlist..."):
            watchlist = run_async(fetch_watchlist())

        def handle_add(symbol, asset_type):
            """Handle adding asset to watchlist."""
            from dashboard.utils.data_fetch import add_to_watchlist
            run_async(add_to_watchlist(symbol, asset_type))
            st.rerun()

        def handle_remove(symbol):
            """Handle removing asset from watchlist."""
            from dashboard.utils.data_fetch import remove_from_watchlist
            run_async(remove_from_watchlist(symbol))
            st.rerun()

        render_watchlist_manager(watchlist, on_add=handle_add, on_remove=handle_remove)


if __name__ == "__main__":
    main()