"""Base LLM client with common functionality."""
import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger
import httpx

from config.settings import settings
from src.agents.base import RateLimiter


@dataclass
class LLMResponse:
    """LLM response container."""

    content: str
    model: str
    provider: str
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    raw_response: Dict[str, Any] = field(default_factory=dict)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, provider: str, model: str, rate_limit_rpm: int = 60):
        self.provider = provider
        self.model = model
        self.rate_limiter = RateLimiter(rate_limit_rpm)
        self.http_client: Optional[httpx.AsyncClient] = None
        self.total_tokens_used = 0
        self.total_cost_usd = 0.0

    async def __aenter__(self) -> "LLMClient":
        self.http_client = httpx.AsyncClient(timeout=60.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.http_client:
            await self.http_client.aclose()

    async def initialize(self) -> None:
        """Initialize the client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=60.0)

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[str] = None,
    ) -> LLMResponse:
        """Send completion request to LLM."""
        pass

    async def complete_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Send completion request and parse JSON response."""
        response = await self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Raw content: {response.content}")
            return {"error": "Failed to parse response", "raw": response.content}

    def track_usage(self, tokens: int, cost: float = 0.0) -> None:
        """Track token usage and cost."""
        self.total_tokens_used += tokens
        self.total_cost_usd += cost

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "provider": self.provider,
            "model": self.model,
            "total_tokens": self.total_tokens_used,
            "total_cost_usd": round(self.total_cost_usd, 4),
        }