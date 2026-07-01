"""FastAPI routes for the Financial News Analyzer."""
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from config.settings import settings
from src.db.mongodb import MongoDB, get_database
from src.db.repositories import (
    NewsRepository,
    MarketDataRepository,
    SentimentRepository,
    ImpactRepository,
    AlertRepository,
    WatchlistRepository,
    JobRunRepository,
    UserRepository,
)
from src.api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


app = FastAPI(
    title="Financial News AI Analyzer",
    description="AI-powered financial news analysis with market data and smart alerts",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document for JSON response."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
        doc["id"] = doc["_id"]
    for key in ("created_at", "published_at", "timestamp", "sent_at", "started_at", "completed_at"):
        if key in doc and doc[key] is not None:
            doc[key] = doc[key].isoformat() if isinstance(doc[key], datetime) else doc[key]
    return doc


# Health endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    mongo_ok = await MongoDB.ping()
    return {
        "status": "healthy" if mongo_ok else "degraded",
        "mongodb": "connected" if mongo_ok else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    mongo_ok = await MongoDB.ping()
    if not mongo_ok:
        raise HTTPException(status_code=503, detail="MongoDB not available")
    return {"status": "ready"}


@app.get("/api/health/system")
async def system_health():
    """System health dashboard data."""
    stats = await MongoDB.get_stats()
    job_repo = JobRunRepository()
    recent_runs = await job_repo.get_recent_runs(limit=10)
    for run in recent_runs:
        _serialize_doc(run)
    return {
        "database": stats,
        "recent_agent_runs": recent_runs,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Auth endpoints
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/auth/register")
async def auth_register(request: RegisterRequest):
    repo = UserRepository()
    existing = await repo.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user_id = await repo.create_user(
        request.username, request.email, hash_password(request.password)
    )
    if not user_id:
        raise HTTPException(status_code=400, detail="Registration failed")
    token = create_access_token({"sub": user_id, "username": request.username})
    return {"token": token, "user": {"id": user_id, "username": request.username}}


@app.post("/api/auth/login")
async def auth_login(request: LoginRequest):
    repo = UserRepository()
    user = await repo.get_by_username(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["_id"]), "username": request.username})
    return {"token": token, "user": {"id": str(user["_id"]), "username": request.username}}


@app.get("/api/auth/me")
async def auth_me(user: dict = Depends(get_current_user)):
    repo = UserRepository()
    from bson import ObjectId
    user_doc = await repo.find_one({"_id": ObjectId(user["sub"])})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    _serialize_doc(user_doc)
    user_doc.pop("hashed_password", None)
    return user_doc


# News endpoints
@app.get("/api/news")
async def get_news(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
    ticker: Optional[str] = None,
):
    """Get news articles - auto-fetches if DB is empty."""
    repo = NewsRepository()
    if ticker:
        articles = await repo.get_by_ticker(ticker, limit=limit)
    else:
        articles = await repo.get_recent(hours=hours, limit=limit)

    if not articles:
        try:
            from src.agents.news_collector import NewsCollectorAgent
            agent = NewsCollectorAgent()
            result = await agent.run()
            logger.info(f"Auto-fetch news: {result.status} ({result.items_new} new)")
            if ticker:
                articles = await repo.get_by_ticker(ticker, limit=limit)
            else:
                articles = await repo.get_recent(hours=hours, limit=limit)
        except Exception as e:
            logger.error(f"Auto-fetch news failed: {e}")

    for a in articles:
        _serialize_doc(a)
    return {"articles": articles, "count": len(articles)}


@app.get("/api/news/{news_id}")
async def get_news_by_id(news_id: str):
    """Get a specific news article."""
    repo = NewsRepository()
    from bson import ObjectId
    article = await repo.find_one({"_id": ObjectId(news_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    _serialize_doc(article)
    return article


# Market data endpoints
@app.get("/api/market")
async def get_market_data(
    symbols: Optional[List[str]] = Query(None),
):
    """Get market data for symbols."""
    repo = MarketDataRepository()
    if symbols:
        data = await repo.get_latest_batch(symbols)
    else:
        all_symbols = await repo.get_all_symbols()
        data = await repo.get_latest_batch(all_symbols[:50])
    for item in data:
        _serialize_doc(item)
    return {"data": data, "count": len(data)}


@app.get("/api/market/{symbol}")
async def get_market_by_symbol(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
):
    """Get market data history for a symbol."""
    repo = MarketDataRepository()
    data = await repo.get_history(symbol, hours=hours)
    for item in data:
        _serialize_doc(item)
    return {"symbol": symbol, "data": data, "count": len(data)}


# Sentiment endpoints
@app.get("/api/sentiment")
async def get_sentiment(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
):
    """Get sentiment analyses."""
    repo = SentimentRepository()
    analyses = await repo.get_recent(hours=hours, limit=limit)
    for item in analyses:
        _serialize_doc(item)
    return {"analyses": analyses, "count": len(analyses)}


@app.get("/api/sentiment/distribution")
async def get_sentiment_distribution(
    hours: int = Query(24, ge=1, le=168),
):
    """Get sentiment distribution."""
    repo = SentimentRepository()
    distribution = await repo.get_sentiment_distribution(hours=hours)
    return {"distribution": distribution, "hours": hours}


@app.get("/api/sentiment/trend")
async def get_sentiment_trend(
    hours: int = Query(24, ge=1, le=168),
    interval: int = Query(60, ge=15, le=480),
):
    """Get sentiment trend bucketed by time intervals."""
    repo = SentimentRepository()
    trend = await repo.get_sentiment_trend(hours=hours, interval_minutes=interval)
    return {"trend": trend, "hours": hours, "interval": interval}


# Impact endpoints
@app.get("/api/impact")
async def get_impact(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
):
    """Get impact analyses."""
    repo = ImpactRepository()
    analyses = await repo.get_high_impact(hours=hours, limit=limit)
    for item in analyses:
        _serialize_doc(item)
    return {"analyses": analyses, "count": len(analyses)}


@app.get("/api/impact/symbol/{symbol}")
async def get_impact_by_symbol(
    symbol: str,
    hours: int = Query(24, ge=1, le=168),
):
    """Get impact analyses for a symbol."""
    repo = ImpactRepository()
    analyses = await repo.get_by_symbol(symbol, hours=hours)
    for item in analyses:
        _serialize_doc(item)
    return {"symbol": symbol, "analyses": analyses, "count": len(analyses)}


@app.get("/api/impact/summary")
async def get_impact_summary(
    hours: int = Query(24, ge=1, le=168),
):
    """Get impact analysis summary."""
    repo = ImpactRepository()
    summary = await repo.get_impact_summary(hours=hours)
    return {"summary": summary, "hours": hours}


# Alert endpoints
@app.get("/api/alerts")
async def get_alerts(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
    channel: Optional[str] = None,
):
    """Get alert history."""
    repo = AlertRepository()
    if channel:
        alerts = await repo.get_by_channel(channel, hours=hours, limit=limit)
    else:
        alerts = await repo.get_recent(hours=hours, limit=limit)
    for item in alerts:
        _serialize_doc(item)
    return {"alerts": alerts, "count": len(alerts)}


# Watchlist endpoints
@app.get("/api/watchlist")
async def get_watchlist():
    """Get user watchlist."""
    repo = WatchlistRepository()
    watchlist = await repo.get_user_watchlist()
    for item in watchlist:
        _serialize_doc(item)
    return {"watchlist": watchlist, "count": len(watchlist)}


class AddWatchlistRequest(BaseModel):
    symbol: str
    asset_type: str = "stock"
    alert_on: List[str] = ["high", "medium"]


@app.post("/api/watchlist")
async def add_to_watchlist(request: AddWatchlistRequest):
    """Add symbol to watchlist."""
    repo = WatchlistRepository()
    item_id = await repo.add_to_watchlist(
        symbol=request.symbol,
        asset_type=request.asset_type,
        alert_on=request.alert_on,
    )
    return {"id": item_id, "symbol": request.symbol, "status": "added"}


@app.delete("/api/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str):
    """Remove symbol from watchlist."""
    repo = WatchlistRepository()
    removed = await repo.remove_from_watchlist(symbol)
    if not removed:
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
    return {"symbol": symbol, "status": "removed"}


# Source Credibility
@app.get("/api/sources/credibility")
async def get_source_credibility():
    """Get news source credibility scores."""
    repo = SentimentRepository()
    sources = await repo.get_source_credibility()
    return {"sources": sources, "count": len(sources)}


# Portfolio Risk
class Holding(BaseModel):
    symbol: str
    weight: float
    asset_type: str = "stock"


class PortfolioRiskRequest(BaseModel):
    holdings: List[Holding]


@app.post("/api/portfolio/risk")
async def calculate_portfolio_risk(request: PortfolioRiskRequest):
    """Calculate portfolio risk metrics."""
    if not request.holdings:
        raise HTTPException(status_code=400, detail="No holdings provided")

    market_repo = MarketDataRepository()
    total_weight = sum(h.weight for h in request.holdings)
    if total_weight == 0:
        total_weight = 1.0

    normalized = [(h.symbol, h.weight / total_weight) for h in request.holdings]
    risk_breakdown = []
    portfolio_volatility = 0.0

    for symbol, weight in normalized:
        history = await market_repo.get_price_history(symbol, hours=168)
        prices = [h["price"] for h in history if "price" in h]
        if len(prices) < 2:
            risk_breakdown.append({
                "symbol": symbol,
                "weight": round(weight * 100, 1),
                "volatility": 0.0,
                "var_95": 0.0,
                "contribution": 0.0,
            })
            continue

        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance) * math.sqrt(252)
        sorted_returns = sorted(returns)
        var_index = max(0, int(len(sorted_returns) * 0.05) - 1)
        var_95 = abs(sorted_returns[var_index])

        contribution = weight * volatility
        portfolio_volatility += contribution ** 2

        risk_breakdown.append({
            "symbol": symbol,
            "weight": round(weight * 100, 1),
            "volatility": round(volatility, 4),
            "var_95": round(var_95, 4),
            "contribution": round(contribution, 4),
        })

    portfolio_volatility = math.sqrt(portfolio_volatility)
    sharpe = 0.0
    if portfolio_volatility > 0:
        sharpe = (0.10 - 0.04) / portfolio_volatility

    num_holdings = len(request.holdings)
    diversification = 1.0 - (sum((h.weight / total_weight) ** 2 for h in request.holdings))

    return {
        "portfolio_volatility": round(portfolio_volatility, 4),
        "sharpe_ratio": round(sharpe, 4),
        "var_95": round(portfolio_volatility * 1.645, 4),
        "diversification_score": round(max(0, diversification), 4),
        "risk_breakdown": risk_breakdown,
    }


# Correlation
@app.get("/api/correlation")
async def get_correlation(
    symbols: str = Query("AAPL,MSFT,GOOGL,NVDA,TSLA"),
    hours: int = Query(72, ge=1, le=168),
):
    """Get asset correlation matrix."""
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    if len(symbol_list) < 2:
        raise HTTPException(status_code=400, detail="At least 2 symbols required")
    repo = MarketDataRepository()
    result = await repo.get_correlation_matrix(symbol_list, hours)
    return result


# Backtest
class BacktestRequest(BaseModel):
    symbol: str
    strategy: str = "sentiment_follow"
    hours: int = 168
    initial_capital: float = 10000.0


@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    """Run a simple strategy backtest."""
    market_repo = MarketDataRepository()
    sentiment_repo = SentimentRepository()

    prices_data = await market_repo.get_price_history(request.symbol, hours=request.hours)
    if len(prices_data) < 3:
        raise HTTPException(status_code=400, detail="Insufficient price data")

    prices = [(p["timestamp"], p["price"]) for p in prices_data if "price" in p]
    sentiments = await sentiment_repo.get_recent(hours=request.hours, limit=500)

    sent_map: Dict[str, float] = {}
    for s in sentiments:
        ts = s.get("created_at")
        if ts:
            hour_key = ts.strftime("%Y-%m-%d-%H")
            val = 1.0 if s["sentiment"] == "bullish" else (-1.0 if s["sentiment"] == "bearish" else 0.0)
            sent_map[hour_key] = val

    capital = request.initial_capital
    position = 0.0
    equity_curve = [{"timestamp": prices[0][0].isoformat(), "equity": capital}]
    trades = 0

    for i in range(1, len(prices)):
        ts, price = prices[i]
        prev_price = prices[i - 1][1]
        price_change = (price - prev_price) / prev_price

        hour_key = ts.strftime("%Y-%m-%d-%H")
        sent_score = sent_map.get(hour_key, 0.0)

        signal = 0.0
        if request.strategy == "sentiment_follow":
            signal = sent_score
        elif request.strategy == "sentiment_contrarian":
            signal = -sent_score
        elif request.strategy == "momentum":
            signal = 1.0 if price_change > 0 else -1.0

        if signal > 0.3 and position <= 0:
            if position < 0:
                capital += position * price * -1
                trades += 1
            buy_amount = capital * 0.95
            position = buy_amount / price
            capital -= buy_amount
            trades += 1
        elif signal < -0.3 and position >= 0:
            if position > 0:
                capital += position * price
                position = 0
                trades += 1

        total_equity = capital + (position * price if position > 0 else 0)
        equity_curve.append({
            "timestamp": ts.isoformat(),
            "equity": round(total_equity, 2),
        })

    if position > 0:
        capital += position * prices[-1][1]
        position = 0

    final_equity = capital
    total_return = (final_equity - request.initial_capital) / request.initial_capital
    equities = [e["equity"] for e in equity_curve]
    max_drawdown = 0.0
    peak = equities[0]
    for eq in equities:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak if peak > 0 else 0
        if dd > max_drawdown:
            max_drawdown = dd

    returns_list = [
        (equities[i] - equities[i - 1]) / equities[i - 1]
        for i in range(1, len(equities))
        if equities[i - 1] > 0
    ]
    avg_return = sum(returns_list) / len(returns_list) if returns_list else 0
    std_return = (
        math.sqrt(sum((r - avg_return) ** 2 for r in returns_list) / len(returns_list))
        if returns_list else 1
    )
    sharpe = (avg_return * 252) / (std_return * math.sqrt(252)) if std_return > 0 else 0

    return {
        "symbol": request.symbol,
        "strategy": request.strategy,
        "initial_capital": request.initial_capital,
        "final_capital": round(final_equity, 2),
        "total_return": round(total_return, 4),
        "sharpe_ratio": round(sharpe, 4),
        "max_drawdown": round(max_drawdown, 4),
        "total_trades": trades,
        "equity_curve": equity_curve,
    }


# Cron endpoints for Vercel
@app.get("/api/cron/collect-news")
async def cron_collect_news():
    """Cron job: Collect news."""
    try:
        from src.agents.news_collector import NewsCollectorAgent
        agent = NewsCollectorAgent()
        result = await agent.run()
        return result.to_dict()
    except Exception as e:
        logger.error(f"Cron collect-news failed: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/api/cron/collect-market")
async def cron_collect_market():
    """Cron job: Collect market data."""
    try:
        from src.agents.market_collector import MarketDataCollectorAgent
        agent = MarketDataCollectorAgent()
        result = await agent.run()
        return result.to_dict()
    except Exception as e:
        logger.error(f"Cron collect-market failed: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/api/cron/analyze-sentiment")
async def cron_analyze_sentiment():
    """Cron job: Analyze sentiment."""
    try:
        from src.agents.sentiment_analyzer import SentimentAnalyzerAgent
        agent = SentimentAnalyzerAgent()
        result = await agent.run()
        return result.to_dict()
    except Exception as e:
        logger.error(f"Cron analyze-sentiment failed: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/api/cron/map-impact")
async def cron_map_impact():
    """Cron job: Map impact."""
    try:
        from src.agents.impact_mapper import ImpactMapperAgent
        agent = ImpactMapperAgent()
        result = await agent.run()
        return result.to_dict()
    except Exception as e:
        logger.error(f"Cron map-impact failed: {e}")
        return {"status": "error", "error": str(e)}


@app.get("/api/cron/check-alerts")
async def cron_check_alerts():
    """Cron job: Check and send alerts."""
    try:
        from src.agents.alert_engine import AlertEngineAgent
        agent = AlertEngineAgent()
        result = await agent.run()
        return result.to_dict()
    except Exception as e:
        logger.error(f"Cron check-alerts failed: {e}")
        return {"status": "error", "error": str(e)}


# Database stats
@app.get("/api/stats")
async def get_stats():
    """Get database statistics."""
    stats = await MongoDB.get_stats()
    return stats


# Price Alerts (user-configurable)
class PriceAlertRequest(BaseModel):
    symbol: str
    target_price: float
    direction: str = "above"  # above or below
    channel: str = "dashboard"  # dashboard, telegram, email


@app.post("/api/alerts/price")
async def create_price_alert(request: PriceAlertRequest):
    """Create a user-configurable price alert."""
    alert_repo = AlertRepository()
    alert_id = await alert_repo.insert_one({
        "impact_id": "price_alert",
        "channel": request.channel,
        "recipient": "user",
        "subject": f"Price Alert: {request.symbol}",
        "body_markdown": f"Alert for {request.symbol} when price goes {request.direction} ${request.target_price}",
        "status": "pending",
        "metadata": {
            "type": "price_alert",
            "symbol": request.symbol,
            "target_price": request.target_price,
            "direction": request.direction,
        },
        "created_at": datetime.utcnow(),
    })
    return {"id": alert_id, "symbol": request.symbol, "status": "created"}


@app.get("/api/alerts/price")
async def get_price_alerts():
    """Get user-configured price alerts."""
    repo = AlertRepository()
    alerts = await repo.find_many(
        filter={"impact_id": "price_alert"},
        sort=[("created_at", -1)],
        limit=50,
    )
    for a in alerts:
        _serialize_doc(a)
    return {"alerts": alerts, "count": len(alerts)}


@app.delete("/api/alerts/price/{alert_id}")
async def delete_price_alert(alert_id: str):
    """Delete a price alert."""
    from bson import ObjectId
    repo = AlertRepository()
    await repo.delete_one({"_id": ObjectId(alert_id), "impact_id": "price_alert"})
    return {"id": alert_id, "status": "deleted"}


# Sentiment by ticker (for heatmap)
@app.get("/api/sentiment/by-ticker")
async def get_sentiment_by_ticker(hours: int = Query(24, ge=1, le=168)):
    """Get sentiment distribution grouped by ticker for heatmap."""
    repo = SentimentRepository()
    news_repo = NewsRepository()
    since = datetime.utcnow() - timedelta(hours=hours)

    recent_news = await news_repo.find_many(
        filter={"created_at": {"$gte": since}},
        sort=[("created_at", -1)],
        limit=500,
    )

    ticker_sentiment: Dict[str, Dict[str, int]] = {}
    for article in recent_news:
        tickers = article.get("tickers", [])
        for ticker in tickers:
            if ticker not in ticker_sentiment:
                ticker_sentiment[ticker] = {"bullish": 0, "bearish": 0, "neutral": 0}
            sentiment = article.get("sentiment", "neutral")
            ticker_sentiment[ticker][sentiment] = ticker_sentiment[ticker].get(sentiment, 0) + 1

    result = [
        {"ticker": t, **counts}
        for t, counts in sorted(ticker_sentiment.items(), key=lambda x: sum(x[1].values()), reverse=True)[:30]
    ]
    return {"tickers": result}


# News volume vs price
@app.get("/api/news/volume-price")
async def get_news_volume_vs_price(
    symbol: str = Query("AAPL"),
    hours: int = Query(72, ge=1, le=168),
):
    """Get news volume correlated with price changes."""
    news_repo = NewsRepository()
    market_repo = MarketDataRepository()

    prices = await market_repo.get_price_history(symbol, hours=hours)
    price_data = {p["timestamp"].strftime("%Y-%m-%d-%H"): p["price"] for p in prices if "price" in p}

    all_news = await news_repo.get_recent(hours=hours, limit=500)
    news_by_hour: Dict[str, int] = {}
    for n in all_news:
        ts = n.get("published_at") or n.get("created_at")
        if ts:
            hour_key = ts.strftime("%Y-%m-%d-%H")
            news_by_hour[hour_key] = news_by_hour.get(hour_key, 0) + 1

    merged = []
    all_hours = sorted(set(list(price_data.keys()) + list(news_by_hour.keys())))
    for h in all_hours:
        merged.append({
            "hour": h,
            "price": price_data.get(h),
            "news_count": news_by_hour.get(h, 0),
        })

    return {"symbol": symbol, "data": merged}


# Sentiment confidence distribution
@app.get("/api/sentiment/confidence-distribution")
async def get_confidence_distribution(hours: int = Query(24, ge=1, le=168)):
    """Get distribution of sentiment confidence scores."""
    repo = SentimentRepository()
    analyses = await repo.get_recent(hours=hours, limit=500)

    buckets = {"0-10": 0, "10-20": 0, "20-30": 0, "30-40": 0, "40-50": 0, "50-60": 0, "60-70": 0, "70-80": 0, "80-90": 0, "90-100": 0}
    for a in analyses:
        conf = a.get("confidence", 0) * 100
        if conf < 10:
            buckets["0-10"] += 1
        elif conf < 20:
            buckets["10-20"] += 1
        elif conf < 30:
            buckets["20-30"] += 1
        elif conf < 40:
            buckets["30-40"] += 1
        elif conf < 50:
            buckets["40-50"] += 1
        elif conf < 60:
            buckets["50-60"] += 1
        elif conf < 70:
            buckets["60-70"] += 1
        elif conf < 80:
            buckets["70-80"] += 1
        elif conf < 90:
            buckets["80-90"] += 1
        else:
            buckets["90-100"] += 1

    return {"distribution": [{"range": k, "count": v} for k, v in buckets.items()]}


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
async def chat_interaction(request: ChatRequest):
    """Chatbot endpoint utilizing live market and news context."""
    from src.ai.openrouter_client import OpenRouterClient

    news_repo = NewsRepository()
    market_repo = MarketDataRepository()

    recent_news = await news_repo.get_recent(hours=24, limit=5)
    all_symbols = await market_repo.get_all_symbols()
    market_data = await market_repo.get_latest_batch(all_symbols)

    news_context = "\n".join([
        f"- {n.get('title')} (Source: {n.get('source')}, Tickers: {', '.join(n.get('tickers', []))})"
        for n in recent_news
    ])

    market_context = "\n".join([
        f"- {m.get('symbol')}: ${m.get('price')} (24h Change: {m.get('change_pct_24h') or m.get('change_pct') or 0}%)"
        for m in market_data
    ])

    system_prompt = (
        "You are the Neural Engine AI Assistant, an expert financial analyst. "
        "You help users analyze recent financial news, market sentiments, and risk impacts. "
        "Use the following live market and news context to answer the user's queries:\n\n"
        f"--- Live Market Prices ---\n{market_context}\n\n"
        f"--- Recent News ---\n{news_context}\n\n"
        "Keep your answers concise, professional, and visually structured."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message}
    ]

    try:
        async with OpenRouterClient() as client:
            response = await client.complete(messages=messages, temperature=0.5, max_tokens=800)
            return {"reply": response.content}
    except Exception as e:
        logger.error(f"Chatbot inference failed: {e}")
        return {
            "reply": (
                "I'm currently operating in offline mode as the AI model inference failed. "
                f"However, I can confirm that the MongoDB database has {len(recent_news)} recent articles "
                f"and {len(market_data)} active market symbols tracked. Error details: {str(e)}"
            )
        }