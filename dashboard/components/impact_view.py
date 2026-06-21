"""Impact view component with glassmorphism styling."""
import streamlit as st
from typing import Any, Dict, List


def render_impact_view(impacts: List[Dict[str, Any]]) -> None:
    """Render the impact analysis view."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h2 style="margin: 0; color: var(--text-primary);">🎯 Impact Analysis</h2>
            <span style="color: var(--text-tertiary); font-size: 0.85rem;">Asset correlation mapping</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not impacts:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">🎯</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">No impact data yet</h3>
                <p style="color: var(--text-secondary);">The Impact Mapper agent will correlate news with assets.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for impact in impacts[:10]:
        news_title = impact.get("news_title", "Unknown")[:80]
        affected_assets = impact.get("affected_assets", [])
        impact_score = impact.get("impact_score", 0)
        risk_level = impact.get("risk_level", "low")
        reasoning = impact.get("reasoning", "")

        # Color coding for impact score
        if impact_score >= 7:
            score_color = "#DC2626"
            score_bg = "rgba(220,38,38,0.1)"
        elif impact_score >= 4:
            score_color = "#F59E0B"
            score_bg = "rgba(245,158,11,0.1)"
        else:
            score_color = "#16A34A"
            score_bg = "rgba(22,163,74,0.1)"

        # Build asset chips with direction
        asset_chips = ""
        for asset in affected_assets[:5]:
            symbol = asset.get("symbol", "")
            direction = asset.get("direction", "neutral")
            direction_emoji = "📈" if direction == "bullish" else "📉" if direction == "bearish" else "➡️"
            direction_class = direction if direction in ["bullish", "bearish"] else "neutral"
            asset_chips += f"""
                <span class="asset-chip {direction_class}" style="font-size: 0.75rem; padding: 4px 10px;">
                    {direction_emoji} {symbol}
                </span>
            """

        # Risk badge
        risk_emoji = "🔴" if risk_level == "high" else "🟡" if risk_level == "medium" else "🟢"

        st.markdown(
            f"""
            <div class="impact-card {risk_level}" style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1rem; color: var(--text-primary); margin-bottom: 4px;">
                            {news_title}...
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <div class="impact-score" style="background: {score_bg}; color: {score_color}; padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 1.1rem;">
                            {impact_score}/10
                        </div>
                        <span class="risk-badge {risk_level}" style="white-space: nowrap;">
                            {risk_emoji} {risk_level.upper()}
                        </span>
                    </div>
                </div>
                {"<div style='color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 12px; line-height: 1.5;'>" + reasoning[:200] + "</div>" if reasoning else ""}
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="color: var(--text-tertiary); font-size: 0.8rem; margin-right: 4px;">Affected:</span>
                    {asset_chips}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )