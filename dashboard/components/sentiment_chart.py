"""Sentiment chart component with glassmorphism styling."""
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from typing import Any, Dict, List


def render_sentiment_chart(sentiments: List[Dict[str, Any]]) -> None:
    """Render the sentiment distribution chart."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
            <h2 style="margin: 0; color: var(--text-primary);">📊 Sentiment Distribution</h2>
            <span style="color: var(--text-tertiary); font-size: 0.85rem;">Last 24h analysis</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not sentiments:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h3 style="color: var(--text-primary); margin-bottom: 8px;">No sentiment data yet</h3>
                <p style="color: var(--text-secondary);">The Sentiment Analyzer agent will process news articles.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    bullish = sum(1 for s in sentiments if s.get("sentiment", "neutral") == "bullish")
    bearish = sum(1 for s in sentiments if s.get("sentiment", "neutral") == "bearish")
    neutral = len(sentiments) - bullish - bearish

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=["Bullish", "Bearish", "Neutral"],
        values=[bullish, bearish, neutral],
        hole=0.6,
        marker=dict(colors=["#16A34A", "#DC2626", "#F59E0B"]),
        textfont=dict(size=14, color="#F8FAFC"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
    ))

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color="#F8FAFC", size=12),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=20, r=20, t=20, b=40),
        annotations=[dict(
            text=f"<b>{len(sentiments)}</b><br>Total",
            x=0.5, y=0.5,
            font=dict(size=20, color="#F8FAFC"),
            showarrow=False,
        )],
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_timeline(timeline_data: List[Dict[str, Any]]) -> None:
    """Render a sentiment timeline chart."""
    if not timeline_data:
        return

    timestamps = [d.get("timestamp", "") for d in timeline_data]
    scores = [d.get("score", 0) for d in timeline_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=scores,
        mode="lines+markers",
        line=dict(color="#60A5FA", width=2),
        marker=dict(size=6, color="#60A5FA"),
        fill="tozeroy",
        fillcolor="rgba(96,165,250,0.1)",
    ))

    fig.update_layout(
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.1)",
            color="#94A3B8",
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.1)",
            color="#94A3B8",
            range=[-1, 1],
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(l=20, r=20, t=10, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)