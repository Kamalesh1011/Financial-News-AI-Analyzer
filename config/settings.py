"""Application settings using Pydantic BaseSettings."""
import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db: str = Field(default="finnews", alias="MONGODB_DB")

    # Market Data APIs
    finnhub_api_key: str = Field(default="", alias="FINNHUB_API_KEY")
    newsapi_api_key: Optional[str] = Field(default=None, alias="NEWSAPI_API_KEY")
    coingecko_api_key: Optional[str] = Field(default=None, alias="COINGECKO_API_KEY")

    # LLM APIs
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    nim_api_key: Optional[str] = Field(default=None, alias="NIM_API_KEY")

    # Alert Channels
    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, alias="TELEGRAM_CHAT_ID")
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, alias="SMTP_USER")
    smtp_pass: Optional[str] = Field(default=None, alias="SMTP_PASS")
    alert_email_to: Optional[str] = Field(default=None, alias="ALERT_EMAIL_TO")

    # Agent Configuration
    news_fetch_interval_minutes: int = Field(default=5, alias="NEWS_FETCH_INTERVAL_MINUTES")
    market_fetch_interval_minutes: int = Field(default=2, alias="MARKET_FETCH_INTERVAL_MINUTES")
    sentiment_batch_size: int = Field(default=15, alias="SENTIMENT_BATCH_SIZE")
    alert_cooldown_minutes: int = Field(default=30, alias="ALERT_COOLDOWN_MINUTES")
    max_alerts_per_hour: int = Field(default=20, alias="MAX_ALERTS_PER_HOUR")

    # Risk Thresholds
    high_risk_confidence_threshold: float = Field(default=0.75, alias="HIGH_RISK_CONFIDENCE_THRESHOLD")
    medium_risk_confidence_threshold: float = Field(default=0.55, alias="MEDIUM_RISK_CONFIDENCE_THRESHOLD")
    sentiment_confidence_threshold: float = Field(default=0.6, alias="SENTIMENT_CONFIDENCE_THRESHOLD")

    # Rate Limits (requests per minute)
    finnhub_rate_limit: int = Field(default=60, alias="FINNHUB_RATE_LIMIT")
    newsapi_rate_limit: int = Field(default=100, alias="NEWSAPI_RATE_LIMIT")
    coingecko_rate_limit: int = Field(default=100, alias="COINGECKO_RATE_LIMIT")
    binance_rate_limit: int = Field(default=1200, alias="BINANCE_RATE_LIMIT")
    openrouter_rate_limit: int = Field(default=100, alias="OPENROUTER_RATE_LIMIT")
    nim_rate_limit: int = Field(default=60, alias="NIM_RATE_LIMIT")

    # Model Preferences
    primary_llm_provider: str = Field(default="openrouter", alias="PRIMARY_LLM_PROVIDER")
    fallback_llm_provider: str = Field(default="nim", alias="FALLBACK_LLM_PROVIDER")
    openrouter_model: str = Field(default="auto", alias="OPENROUTER_MODEL")
    nim_model: str = Field(default="nemotron-3-ultra", alias="NIM_MODEL")

    # JWT Authentication
    jwt_secret: str = Field(default="neural-engine-dev-secret-change-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")

    # Vercel/Streamlit
    streamlit_server_port: int = Field(default=8501, alias="STREAMLIT_SERVER_PORT")
    streamlit_server_address: str = Field(default="0.0.0.0", alias="STREAMLIT_SERVER_ADDRESS")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()

    @field_validator("primary_llm_provider", "fallback_llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        allowed = {"openrouter", "nim", "openai", "anthropic"}
        if v.lower() not in allowed:
            raise ValueError(f"LLM provider must be one of {allowed}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_user and self.smtp_pass and self.alert_email_to)

    @property
    def openrouter_enabled(self) -> bool:
        return bool(self.openrouter_api_key)

    @property
    def nim_enabled(self) -> bool:
        return bool(self.nim_api_key)

    @property
    def newsapi_enabled(self) -> bool:
        return bool(self.newsapi_api_key)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()