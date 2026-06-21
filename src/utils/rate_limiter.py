"""Rate limiting utilities."""
import asyncio
import time
from collections import defaultdict
from typing import Dict, Optional


class TokenBucketLimiter:
    """Token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, waiting if necessary. Returns wait time in seconds."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0
            else:
                wait_time = (tokens - self.tokens) / self.refill_rate
                self.tokens = 0
                self.last_refill = now + wait_time
                return wait_time

    def get_status(self) -> dict:
        return {
            "tokens": int(self.tokens),
            "capacity": self.capacity,
            "refill_rate": self.refill_rate,
        }


class MultiEndpointLimiter:
    """Rate limiter for multiple API endpoints."""

    def __init__(self):
        self._limiters: Dict[str, TokenBucketLimiter] = {}

    def configure(
        self, endpoint: str, requests_per_minute: int, burst_size: Optional[int] = None
    ) -> None:
        capacity = burst_size or requests_per_minute
        refill_rate = requests_per_minute / 60.0
        self._limiters[endpoint] = TokenBucketLimiter(capacity, refill_rate)

    async def acquire(self, endpoint: str) -> float:
        if endpoint not in self._limiters:
            return 0.0
        return await self._limiters[endpoint].acquire()

    def get_status(self) -> Dict[str, dict]:
        return {k: v.get_status() for k, v in self._limiters.items()}