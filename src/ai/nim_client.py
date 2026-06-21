"""NVIDIA NIM API client for LLM inference."""
import time
from typing import Any, Dict, List, Optional
from loguru import logger

from .llm_client import LLMClient, LLMResponse
from config.settings import settings
from config.constants import NIM_BASE_URL


class NIMClient(LLMClient):
    """NVIDIA NIM API client for hosted models."""

    def __init__(self, model: str = "nemotron-3-ultra"):
        super().__init__(
            provider="nim",
            model=model or settings.nim_model,
            rate_limit_rpm=settings.nim_rate_limit,
        )
        self.api_key = settings.nim_api_key

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[str] = None,
    ) -> LLMResponse:
        """Send completion request to NVIDIA NIM."""
        if not self.api_key:
            raise ValueError("NIM API key not configured")

        await self.rate_limiter.acquire()

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        start_time = time.monotonic()
        try:
            response = await self.http_client.post(
                f"{NIM_BASE_URL}/chat/completions",
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
                provider="nim",
                tokens_used=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                raw_response=data,
            )

        except Exception as e:
            latency_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"NIM request failed: {e}")
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
            logger.error(f"Failed to parse JSON from NIM response: {e}")
            return {"error": "Failed to parse response", "raw": response.content}