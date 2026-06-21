"""Watchlist manager component with glassmorphism styling."""
import streamlit as st
from typing import Any, Dict, List


def render_watchlist_manager(
    watchlist: List[Dict[str, Any]],
    on_add=None,
    on_remove=None,
) -> None:
    """Render the watchlist manager with glass styling."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h2 style="margin: 0; color: var(--text-primary);">👁️ Watchlist</h2>
            <span style="color: var(--text-tertiary); font-size: 0.85rem;">Tracked assets</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add asset form
    with st.expander("➕ Add Asset", expanded=False):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            new_symbol = st.text_input("Symbol", placeholder="e.g., TSLA", label_visibility="collapsed")
        with col2:
            asset_type = st.selectbox("Type", ["stock", "crypto", "forex"], label_visibility="collapsed")
        with col3:
            if st.button("Add", use_container_width=True):
                if new_symbol and on_add:
                    on_add(new_symbol.upper(), asset_type)

    if not watchlist:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">👁️</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">Watchlist is empty</h3>
                <p style="color: var(--text-secondary);">Add assets to track sentiment and impact.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Group by type
    stocks = [w for w in watchlist if w.get("asset_type") in ["stock", None]]
    crypto = [w for w in watchlist if w.get("asset_type") == "crypto"]
    forex = [w for w in watchlist if w.get("asset_type") == "forex"]

    type_emoji = {"stock": "💹", "crypto": "₿", "forex": "💱"}

    for group_name, group, emoji in [
        ("Stocks", stocks, "💹"),
        ("Crypto", crypto, "₿"),
        ("Forex", forex, "💱"),
    ]:
        if not group:
            continue

        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-tertiary); margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 1px;">
                {emoji} {group_name} ({len(group)})
            </div>
            """,
            unsafe_allow_html=True,
        )

        for item in group:
            symbol = item.get("symbol", "")
            asset_type = item.get("asset_type", "stock")

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="market-item neutral" style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; background: rgba(148,163,184,0.05); border: 1px solid rgba(148,163,184,0.1);">
                        <span>{type_emoji.get(asset_type, "📊")}</span>
                        <span style="font-weight: 600; color: var(--text-primary);">{symbol}</span>
                        <span style="color: var(--text-tertiary); font-size: 0.8rem; text-transform: uppercase;">{asset_type}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("🗑️", key=f"remove_{symbol}", help=f"Remove {symbol}"):
                    if on_remove:
                        on_remove(symbol)