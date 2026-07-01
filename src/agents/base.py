"""Base agent class with common functionality."""
import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from loguru import logger
from bson import ObjectId
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import httpx

from config.settings import settings
from src.db.repositories import JobRunRepository


@dataclass
class AgentResult:
    """Result from an agent execution."""

    agent_name: str
    status: str  # success, partial, failed
    items_processed: int = 0
    items_new: int = 0
    items_updated: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    @property
    def duration_ms(self) -> float:
        return self.duration_seconds * 1000

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "items_processed": self.items_processed,
            "items_new": self.items_new,
            "items_updated": self.items_updated,
            "errors": self.errors,
            "metadata": self.metadata,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_minute: int):
        self.rpm = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait if necessary to respect rate limit."""
        async with self._lock:
            now = time.monotonic()
            time_since_last = now - self.last_request_time
            if time_since_last < self.interval:
                wait_time = self.interval - time_since_last
                await asyncio.sleep(wait_time)
            self.last_request_time = time.monotonic()


class BaseAgent(ABC):
    """Base class for all agents in the pipeline."""

    def __init__(self, name: str, rate_limit_rpm: int = 60):
        self.name = name
        self.rate_limiter = RateLimiter(rate_limit_rpm)
        self.job_repo = JobRunRepository()
        self.http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BaseAgent":
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.http_client:
            await self.http_client.aclose()

    async def initialize(self) -> None:
        """Initialize the agent."""
        logger.info(f"Initializing {self.name}...")
        if not self.http_client:
            self.http_client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None

    async def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retries: int = 3,
    ) -> Dict[str, Any]:
        """Make an HTTP request with rate limiting and retry logic."""
        await self.rate_limiter.acquire()

        last_error = None
        for attempt in range(retries):
            try:
                response = await self.http_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                last_error = e
                status_code = e.response.status_code

                if status_code == 429:  # Rate limited
                    retry_after = int(e.response.headers.get("Retry-After", 60))
                    logger.warning(
                        f"{self.name}: Rate limited. Waiting {retry_after}s..."
                    )
                    await asyncio.sleep(retry_after)
                elif status_code >= 500:  # Server error - retry
                    wait_time = 2 ** (attempt + 1)
                    logger.warning(
                        f"{self.name}: Server error {status_code}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:  # Client error - don't retry
                    logger.error(
                        f"{self.name}: HTTP {status_code}: {e.response.text}"
                    )
                    raise

            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                last_error = e
                wait_time = 2 ** (attempt + 1)
                logger.warning(
                    f"{self.name}: Connection error. Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

        raise last_error

    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.make_request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return await self.make_request("POST", url, **kwargs)

    @abstractmethod
    async def execute(self) -> AgentResult:
        """Execute the agent's main logic. Must be implemented by subclasses."""
        pass

    async def run(self) -> AgentResult:
        """Run the agent with logging and job tracking."""
        started_at = datetime.utcnow()
        job_id = None

        try:
            # Log job start
            job_doc = {
                "job_name": self.name,
                "status": "started",
                "started_at": started_at,
                "items_processed": 0,
                "errors": [],
                "metadata": {},
            }
            job_id = await self.job_repo.insert_one(job_doc)
            logger.info(f"🚀 Starting {self.name} (job: {job_id})")

            # Initialize http client if not already done via context manager
            if not self.http_client:
                self.http_client = httpx.AsyncClient(
                    timeout=30.0,
                    follow_redirects=True,
                    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                )

            # Initialize
            await self.initialize()

            # Execute
            result = await self.execute()
            result.started_at = started_at
            result.completed_at = datetime.utcnow()
            result.duration_seconds = (
                result.completed_at - started_at
            ).total_seconds()

            # Update job status
            status = "completed" if result.status != "failed" else "failed"
            await self.job_repo.update_one(
                filter={"_id": ObjectId(job_id)},
                update={
                    "$set": {
                        "status": status,
                        "completed_at": result.completed_at,
                        "duration_seconds": result.duration_seconds,
                        "items_processed": result.items_processed,
                        "errors": result.errors,
                        "metadata": result.metadata,
                    }
                },
            )

            emoji = "✅" if status == "completed" else "❌"
            logger.info(
                f"{emoji} {self.name} {status}: "
                f"{result.items_processed} items in {result.duration_seconds:.1f}s"
            )

            return result

        except Exception as e:
            logger.error(f"❌ {self.name} failed with exception: {e}")
            result = AgentResult(
                agent_name=self.name,
                status="failed",
                errors=[str(e)],
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

            # Update job status
            if job_id:
                try:
                    await self.job_repo.update_one(
                        filter={"_id": ObjectId(job_id)},
                        update={
                            "$set": {
                                "status": "failed",
                                "completed_at": result.completed_at,
                                "duration_seconds": result.duration_seconds,
                                "errors": [str(e)],
                            }
                        },
                    )
                except Exception:
                    pass

            return result

        finally:
            await self.cleanup()


class ParallelAgentRunner:
    """Run multiple agents in parallel."""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent

    async def run_agents(
        self, agents: List[BaseAgent]
    ) -> List[AgentResult]:
        """Run agents in parallel with concurrency limit."""
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def _run_with_semaphore(agent: BaseAgent) -> AgentResult:
            async with semaphore:
                return await agent.run()

        tasks = [_run_with_semaphore(agent) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    AgentResult(
                        agent_name=agents[i].name,
                        status="failed",
                        errors=[str(result)],
                    )
                )
            else:
                final_results.append(result)

        return final_results