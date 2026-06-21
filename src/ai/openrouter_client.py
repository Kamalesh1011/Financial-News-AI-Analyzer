"""OpenRouter API client for LLM inference."""
import time
from typing import Any, Dict, List, Optional
from loguru import logger

from .llm_client import LLMClient, LLMResponse
from config.settings import settings
from config.constants import OPENROUTER_BASE_URL


class OpenRouterClient(LLMClient):
    """OpenRouter API client for multi-model routing."""

    def __init__(self, model: str = "auto"):
        super().__init__(
            provider="openrouter",
            model=model or settings.openrouter_model,
            rate_limit_rpm=settings.openrouter_rate_limit,
        )
        self.api_key = settings.openrouter_api_key

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://financial-news-analyzer.com",
            "X-Title": "Financial News Analyzer",
            "Content-Type": "application/json",
        }

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[str] = None,
    ) -> LLMResponse:
        """Send completion request to OpenRouter."""
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        await self.rate_limiter.acquire()

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        start_time = time.monotonic()
        try:
            response = await self.http_client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            latency_ms = (time.monotonic() - start_time) * 1000

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens

            self.track_usage(total_tokens)

            return LLMResponse(
                content=content,
                model=data.get("model", self.model),
                provider="openrouter",
                tokens_used=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                raw_response=data,
            )

        except Exception as e:
            latency_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"OpenRouter request failed: {e}")
            raise

    async def complete_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Send completion request with JSON output."""
        response = await self.complete(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format="json",
        )

        import json
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenRouter response: {e}")
            return {"error": "Failed to parse response", "raw": response.content}