"""Theme manager for light/dark mode switching."""
import streamlit as st
from pathlib import Path
from typing import Optional


class ThemeManager:
    """Manages light/dark theme switching with persistence."""

    THEMES = {
        "dark": {
            "name": "Obsidian Dark",
            "icon": "🌙",
            "config": {
                "primaryColor": "#60A5FA",
                "backgroundColor": "#0B1120",
                "secondaryBackgroundColor": "#1E293B",
                "textColor": "#F1F5F9",
                "linkColor": "#60A5FA",
                "borderColor": "#334155",
            },
        },
        "light": {
            "name": "Arctic Light",
            "icon": "☀️",
            "config": {
                "primaryColor": "#2563EB",
                "backgroundColor": "#F8FAFC",
                "secondaryBackgroundColor": "#E2E8F0",
                "textColor": "#0F172A",
                "linkColor": "#2563EB",
                "borderColor": "#CBD5E1",
            },
        },
    }

    @staticmethod
    def get_current_theme() -> str:
        """Get the current theme from session state."""
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"
        return st.session_state.theme

    @staticmethod
    def set_theme(theme: str) -> None:
        """Set the theme and update session state."""
        if theme in ThemeManager.THEMES:
            st.session_state.theme = theme
            # Store in localStorage via JavaScript
            st.markdown(
                f"""
                <script>
                    localStorage.setItem('finnews_theme', '{theme}');
                </script>
                """,
                unsafe_allow_html=True,
            )

    @staticmethod
    def toggle_theme() -> None:
        """Toggle between light and dark themes."""
        current = ThemeManager.get_current_theme()
        new_theme = "light" if current == "dark" else "dark"
        ThemeManager.set_theme(new_theme)
        st.rerun()

    @staticmethod
    def inject_theme_css() -> None:
        """Inject theme CSS based on current theme."""
        theme = ThemeManager.get_current_theme()
        theme_css_path = Path(f"dashboard/styles/themes/{theme}.css")

        if theme_css_path.exists():
            css = theme_css_path.read_text()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    @staticmethod
    def inject_theme_attribute() -> None:
        """Inject data-theme attribute to HTML element."""
        theme = ThemeManager.get_current_theme()
        st.markdown(
            f"""
            <script>
                document.documentElement.setAttribute('data-theme', '{theme}');
            </script>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_theme_toggle() -> None:
        """Render the theme toggle in the sidebar."""
        current = ThemeManager.get_current_theme()
        is_dark = current == "dark"

        with st.sidebar:
            st.markdown("---")
            col1, col2 = st.columns([3, 1])

            with col1:
                theme_name = ThemeManager.THEMES[current]["name"]
                theme_icon = ThemeManager.THEMES[current]["icon"]
                st.markdown(f"**{theme_icon} {theme_name}**")

            with col2:
                if st.button(
                    "☀️" if is_dark else "🌙",
                    key="theme_toggle",
                    help="Toggle theme",
                ):
                    ThemeManager.toggle_theme()

    @staticmethod
    def get_theme_css_variables() -> dict:
        """Get CSS variables for the current theme."""
        theme = ThemeManager.get_current_theme()
        return ThemeManager.THEMES[theme]["config"]


def inject_global_styles() -> None:
    """Inject all global styles."""
    # Load main CSS
    main_css_path = Path("dashboard/styles/main.css")
    if main_css_path.exists():
        main_css = main_css_path.read_text()
        st.markdown(f"<style>{main_css}</style>", unsafe_allow_html=True)

    # Load theme CSS
    ThemeManager.inject_theme_css()

    # Inject theme attribute
    ThemeManager.inject_theme_attribute()

    # Load Google Fonts
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )


def render_glass_card(content: str, class_name: str = "glass-card", key: Optional[str] = None) -> None:
    """Render a glass card container."""
    st.markdown(
        f'<div class="{class_name}" key="{key or ""}">{content}</div>',
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_type: str = "neutral",
    icon: str = "",
) -> None:
    """Render a KPI card with 3D effect."""
    delta_html = ""
    if delta:
        delta_class = f"kpi-delta {delta_type}"
        arrow = "↑" if delta_type == "positive" else "↓" if delta_type == "negative" else "→"
        delta_html = f'<span class="{delta_class}">{arrow} {delta}</span>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{icon} {label}</div>
            <div class="kpi-number">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sentiment_badge(sentiment: str, confidence: float = 0.0) -> None:
    """Render a sentiment badge."""
    emoji = "📈" if sentiment == "bullish" else "📉" if sentiment == "bearish" else "➡️"
    confidence_text = f" ({confidence:.0%})" if confidence > 0 else ""
    st.markdown(
        f'<span class="sentiment-badge {sentiment}">{emoji} {sentiment.title()}{confidence_text}</span>',
        unsafe_allow_html=True,
    )


def render_risk_badge(risk_level: str) -> None:
    """Render a risk level badge."""
    emoji = "🔴" if risk_level == "high" else "🟡" if risk_level == "medium" else "🟢"
    st.markdown(
        f'<span class="risk-badge {risk_level}">{emoji} {risk_level.upper()}</span>',
        unsafe_allow_html=True,
    )


def render_asset_chip(symbol: str, direction: str = "neutral", change: float = 0.0) -> None:
    """Render an asset chip with direction."""
    emoji = "📈" if direction == "bullish" else "📉" if direction == "bearish" else "➡️"
    change_text = f" {change:+.2f}%" if change != 0 else ""
    st.markdown(
        f"""
        <span class="asset-chip {direction}">
            {emoji} {symbol}{change_text}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_status_dot(status: str = "online") -> None:
    """Render a status indicator dot."""
    st.markdown(
        f'<span class="status-dot {status}"></span>',
        unsafe_allow_html=True,
    )