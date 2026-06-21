"""Application constants and configuration values."""

# API Base URLs
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
NEWSAPI_BASE_URL = "https://newsapi.org/v2"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

# MongoDB Collection Names
COLLECTION_NAMES = {
    "raw_news": "raw_news",
    "market_data": "market_data",
    "sentiment_analysis": "sentiment_analysis",
    "impact_analysis": "impact_analysis",
    "alerts": "alerts",
    "watchlist": "watchlist",
    "job_runs": "job_runs",
}

# MongoDB Indexes
INDEXES = {
    "raw_news": [
        {"keys": [("url", 1)], "unique": True},
        {"keys": [("published_at", -1)]},
        {"keys": [("source", 1), ("published_at", -1)]},
        {"keys": [("tickers", 1)]},
        {"keys": [("created_at", -1)]},
    ],
    "market_data": [
        {"keys": [("symbol", 1), ("timestamp", -1)]},
        {"keys": [("source", 1), ("timestamp", -1)]},
        {"keys": [("symbol", 1), ("source", 1), ("timestamp", -1)]},
    ],
    "sentiment_analysis": [
        {"keys": [("news_id", 1)]},
        {"keys": [("created_at", -1)]},
        {"keys": [("sentiment", 1), ("confidence", -1)]},
        {"keys": [("model", 1), ("created_at", -1)]},
    ],
    "impact_analysis": [
        {"keys": [("news_id", 1)]},
        {"keys": [("sentiment_id", 1)]},
        {"keys": [("risk_level", 1), ("created_at", -1)]},
        {"keys": [("created_at", -1)]},
    ],
    "alerts": [
        {"keys": [("impact_id", 1)]},
        {"keys": [("channel", 1), ("sent_at", -1)]},
        {"keys": [("status", 1), ("sent_at", -1)]},
    ],
    "watchlist": [
        {"keys": [("user_id", 1), ("symbol", 1)], "unique": True},
        {"keys": [("user_id", 1)]},
    ],
}

# Sentiment Labels
SENTIMENT_LABELS = ["bullish", "bearish", "neutral"]

# Risk Levels
RISK_LEVELS = ["high", "medium", "low"]

# Asset Types
ASSET_TYPES = ["stock", "crypto", "forex", "commodity", "etf"]

# Default Watchlist
DEFAULT_WATCHLIST = [
    {"symbol": "SPY", "asset_type": "etf", "alert_on": ["high", "medium"]},
    {"symbol": "QQQ", "asset_type": "etf", "alert_on": ["high", "medium"]},
    {"symbol": "AAPL", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "MSFT", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "GOOGL", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "AMZN", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "NVDA", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "META", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "TSLA", "asset_type": "stock", "alert_on": ["high", "medium"]},
    {"symbol": "BTC", "asset_type": "crypto", "alert_on": ["high", "medium"]},
    {"symbol": "ETH", "asset_type": "crypto", "alert_on": ["high", "medium"]},
    {"symbol": "SOL", "asset_type": "crypto", "alert_on": ["high", "medium"]},
    {"symbol": "EURUSD=X", "asset_type": "forex", "alert_on": ["high", "medium"]},
    {"symbol": "GBPUSD=X", "asset_type": "forex", "alert_on": ["high", "medium"]},
    {"symbol": "GLD", "asset_type": "commodity", "alert_on": ["high", "medium"]},
]

# News Keywords (for filtering)
NEWS_KEYWORDS = [
    "fed", "federal reserve", "inflation", "cpi", "interest rate", "rate hike", "rate cut",
    "earnings", "revenue", "profit", "loss", "guidance", "outlook",
    "gdp", "recession", "unemployment", "jobs", "payroll",
    "ipo", "merger", "acquisition", "buyout", "deal",
    "ipo", "listing", "delisting", "ban", "sanction",
    "tariff", "trade war", "trade deal", "oil", "crude",
    "bitcoin", "crypto", "etf", "halving", "mining",
    "apple", "microsoft", "google", "amazon", "nvidia", "tesla", "meta",
    "sp500", "nasdaq", "dow jones", "russell", "vix",
]

# Finnhub Endpoints
FINNHUB_ENDPOINTS = {
    "market_news": "/news",
    "company_news": "/company-news",
    "quote": "/quote",
    "stock_profile": "/stock/profile2",
    "search": "/search",
    "peers": "/stock/peers",
    "recommendation": "/stock/recommendation",
    "earnings": "/stock/earnings",
    "basic_financials": "/stock/metric",
    "forex": "/forex/rates",
    "crypto": "/crypto/candle",
    "sentiment": "/news-sentiment",
}

# NewsAPI Endpoints
NEWSAPI_ENDPOINTS = {
    "top_headlines": "/top-headlines",
    "everything": "/everything",
    "sources": "/sources",
}

# CoinGecko Endpoints
COINGECKO_ENDPOINTS = {
    "simple_price": "/simple/price",
    "coins_markets": "/coins/markets",
    "coin_details": "/coins",
    "coin_market_chart": "/coins/{id}/market_chart",
    "trending": "/search/trending",
    "global": "/global",
}

# Binance Endpoints
BINANCE_ENDPOINTS = {
    "ticker_24h": "/ticker/24hr",
    "klines": "/klines",
    "depth": "/depth",
    "trades": "/trades",
    "exchange_info": "/exchangeInfo",
    "avg_price": "/avgPrice",
}

# Symbol Mapping: News API symbols to CoinGecko IDs
CRYPTO_SYMBOL_TO_COINGECKO = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "MATIC": "matic-network",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "FIL": "filecoin",
    "ALGO": "algorand",
    "NEAR": "near",
    "FTM": "fantom",
    "ARB": "arbitrum",
    "OP": "optimism",
}

# Binance Symbol Mapping
CRYPTO_SYMBOL_TO_BINANCE = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
    "ADA": "ADAUSDT",
    "XRP": "XRPUSDT",
    "DOGE": "DOGEUSDT",
    "DOT": "DOTUSDT",
    "AVAX": "AVAXUSDT",
    "LINK": "LINKUSDT",
    "MATIC": "MATICUSDT",
    "UNI": "UNIUSDT",
    "ATOM": "ATOMUSDT",
    "LTC": "LTCUSDT",
    "BCH": "BCHUSDT",
    "FIL": "FILUSDT",
    "ALGO": "ALGOUSDT",
    "NEAR": "NEARUSDT",
    "FTM": "FTMUSDT",
    "ARB": "ARBUSDT",
    "OP": "OPUSDT",
}

# Alert Formats
ALERT_FORMAT_TELEGRAM = """
🚨 **{risk_emoji} HIGH IMPACT ALERT**

📰 **{title}**

💰 **Sentiment:** {sentiment_emoji} {sentiment} ({confidence:.0%})
⚡ **Risk Level:** {risk_emoji} {risk_level}

📈 **Affected Assets:**
{affected_assets}

📝 **AI Analysis:**
{reasoning}

🔗 [Read More]({source_url})
⏱️ {timestamp}
"""

ALERT_FORMAT_EMAIL = """
<h2 style="color: {risk_color};">🚨 {risk_emoji} HIGH IMPACT ALERT</h2>
<h3>{title}</h3>
<table style="border-collapse: collapse; width: 100%;">
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Sentiment</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{sentiment_emoji} {sentiment} ({confidence:.0%})</td>
    </tr>
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Risk Level</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{risk_emoji} {risk_level}</td>
    </tr>
</table>
<h4>Affected Assets</h4>
<table style="border-collapse: collapse; width: 100%;">
    <thead>
        <tr>
            <th style="padding: 8px; border: 1px solid #ddd;">Symbol</th>
            <th style="padding: 8px; border: 1px solid #ddd;">Direction</th>
            <th style="padding: 8px; border: 1px solid #ddd;">Confidence</th>
        </tr>
    </thead>
    <tbody>
        {affected_assets_rows}
    </tbody>
</table>
<h4>AI Analysis</h4>
<p>{reasoning}</p>
<p><a href="{source_url}">Read Full Article</a></p>
<p style="color: #888;">⏱️ {timestamp}</p>
"""

# Risk Emoji Mapping
RISK_EMOJI = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}

# Sentiment Emoji Mapping
SENTIMENT_EMOJI = {
    "bullish": "📈",
    "bearish": "📉",
    "neutral": "➡️",
}

# Direction Emoji Mapping
DIRECTION_EMOJI = {
    "bullish": "📈",
    "bearish": "📉",
    "neutral": "➡️",
}

# Risk Color for Email
RISK_COLOR = {
    "high": "#e74c3c",
    "medium": "#f39c12",
    "low": "#27ae60",
}

# Streamlit Page Config
STREAMLIT_PAGE_CONFIG = {
    "page_title": "Financial News AI Analyzer",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}