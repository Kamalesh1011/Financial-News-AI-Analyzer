"""Market panel component with glassmorphism styling."""
import streamlit as st
from typing import Any, Dict, List


def render_market_panel(market_data: List[Dict[str, Any]]) -> None:
    """Render the market data panel with glass styling."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h2 style="margin: 0; color: var(--text-primary);">📈 Market Overview</h2>
            <span style="color: var(--text-tertiary); font-size: 0.85rem;">Real-time prices</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not market_data:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📈</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">No market data yet</h3>
                <p style="color: var(--text-secondary);">The Market Collector agent will fetch prices automatically.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Group by type
    stocks = [m for m in market_data if m.get("asset_type") in ["stock", "forex"]]
    crypto = [m for m in market_data if m.get("asset_type") == "crypto"]

    # Stocks & Forex
    if stocks:
        st.markdown(
            """
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">
                💹 Stocks & Forex
            </div>
            """,
            unsafe_allow_html=True,
        )

        for asset in stocks[:12]:
            symbol = asset.get("symbol", "")
            price = asset.get("price", 0)
            change_pct = asset.get("change_pct", 0)
            direction = "bullish" if change_pct > 0 else "bearish" if change_pct < 0 else "neutral"
            direction_emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"

            # Color
            if change_pct > 0:
                change_color = "#16A34A"
            elif change_pct < 0:
                change_color = "#DC2626"
            else:
                change_color = "#94A3B8"

            # Format price
            if price >= 1000:
                price_str = f"${price:,.0f}"
            elif price >= 100:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:,.4f}"

            st.markdown(
                f"""
                <div class="market-item {direction}" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; margin-bottom: 6px; border-radius: 8px; background: rgba(148,163,184,0.05); border: 1px solid rgba(148,163,184,0.1);">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span>{direction_emoji}</span>
                        <span style="font-weight: 600; color: var(--text-primary);">{symbol}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">
                            {price_str}
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: {change_color};">
                            {change_pct:+.2f}%
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Crypto
    if crypto:
        st.markdown(
            """
            <div style="font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); margin: 20px 0 12px; text-transform: uppercase; letter-spacing: 1px;">
                ₿ Cryptocurrency
            </div>
            """,
            unsafe_allow_html=True,
        )

        for asset in crypto[:6]:
            symbol = asset.get("symbol", "")
            price = asset.get("price", 0)
            change_pct = asset.get("change_pct", 0)
            direction = "bullish" if change_pct > 0 else "bearish" if change_pct < 0 else "neutral"
            direction_emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"

            if change_pct > 0:
                change_color = "#16A34A"
            elif change_pct < 0:
                change_color = "#DC2626"
            else:
                change_color = "#94A3B8"

            if price >= 10000:
                price_str = f"${price:,.0f}"
            elif price >= 1000:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:,.4f}"

            st.markdown(
                f"""
                <div class="market-item {direction}" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; margin-bottom: 6px; border-radius: 8px; background: rgba(148,163,184,0.05); border: 1px solid rgba(148,163,184,0.1);">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span>{direction_emoji}</span>
                        <span style="font-weight: 600; color: var(--text-primary);">{symbol}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">
                            {price_str}
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: {change_color};">
                            {change_pct:+.2f}%
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )