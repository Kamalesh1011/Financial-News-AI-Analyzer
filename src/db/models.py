"""Pydantic models for MongoDB documents."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from config.constants import SENTIMENT_LABELS, RISK_LEVELS, ASSET_TYPES


class BaseDocument(BaseModel):
    """Base document model."""

    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}


class RawNewsDocument(BaseDocument):
    """Raw news article document."""

    source: str  # finnhub, newsapi
    external_id: str
    title: str
    summary: str
    url: str
    published_at: datetime
    tickers: List[str] = []
    raw_data: Dict[str, Any] = {}

    model_config = {"collection": "raw_news"}


class MarketDataDocument(BaseDocument):
    """Market data snapshot document."""

    symbol: str
    price: float
    change_24h: Optional[float] = None
    change_pct_24h: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: datetime
    source: str  # finnhub, coingecko, binance

    model_config = {"collection": "market_data"}


class SentimentAnalysisDocument(BaseDocument):
    """Sentiment analysis result document."""

    news_id: str  # Reference to RawNewsDocument
    model: str  # openrouter/claude-3.5-sonnet, nim/nemotron-3-ultra
    sentiment: str  # bullish, bearish, neutral
    confidence: float  # 0.0 - 1.0
    key_events: List[str] = []
    reasoning: str
    tokens_used: int = 0
    cost_usd: float = 0.0

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: str) -> str:
        if v.lower() not in SENTIMENT_LABELS:
            raise ValueError(f"Sentiment must be one of {SENTIMENT_LABELS}")
        return v.lower()

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    model_config = {"collection": "sentiment_analysis"}


class AffectedAsset(BaseModel):
    """Affected asset in impact analysis."""

    symbol: str
    direction: str  # bullish, bearish, neutral
    confidence: float
    asset_type: str  # stock, crypto, forex, commodity, etf
    reasoning: Optional[str] = None

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:
        if v.lower() not in SENTIMENT_LABELS:
            raise ValueError(f"Direction must be one of {SENTIMENT_LABELS}")
        return v.lower()

    @field_validator("asset_type")
    @classmethod
    def validate_asset_type(cls, v: str) -> str:
        if v.lower() not in ASSET_TYPES:
            raise ValueError(f"Asset type must be one of {ASSET_TYPES}")
        return v.lower()


class ImpactAnalysisDocument(BaseDocument):
    """Impact analysis result document."""

    news_id: str  # Reference to RawNewsDocument
    sentiment_id: str  # Reference to SentimentAnalysisDocument
    affected_assets: List[AffectedAsset]
    risk_level: str  # high, medium, low
    reasoning: str
    impact_score: float = 0.0  # -1.0 to 1.0

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        if v.lower() not in RISK_LEVELS:
            raise ValueError(f"Risk level must be one of {RISK_LEVELS}")
        return v.lower()

    model_config = {"collection": "impact_analysis"}


class AlertDocument(BaseDocument):
    """Alert document."""

    impact_id: str  # Reference to ImpactAnalysisDocument
    channel: str  # telegram, email
    recipient: str  # chat_id or email
    subject: str
    body_markdown: str
    body_html: Optional[str] = None
    status: str = "pending"  # pending, sent, failed
    sent_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0

    model_config = {"collection": "alerts"}


class WatchlistDocument(BaseDocument):
    """Watchlist entry document."""

    user_id: str
    symbol: str
    asset_type: str
    alert_on: List[str] = ["high", "medium"]
    notes: Optional[str] = None

    model_config = {"collection": "watchlist"}


class JobRunDocument(BaseDocument):
    """Job execution log document."""

    job_name: str
    status: str  # started, completed, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    items_processed: int = 0
    errors: List[str] = []
    metadata: Dict[str, Any] = {}

    model_config = {"collection": "job_runs"}


class UserDocument(BaseDocument):
    """User document for authentication."""

    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    role: str = "user"  # user, admin

    model_config = {"collection": "users"}