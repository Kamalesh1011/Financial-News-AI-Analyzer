"""Content deduplication utilities."""
import hashlib
from typing import List, Set


class ContentDeduplicator:
    """Track and deduplicate content by hash."""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._seen: Set[str] = set()

    @staticmethod
    def compute_hash(title: str, source: str) -> str:
        """Compute a unique hash for a news article."""
        content = f"{title.lower().strip()}:{source.lower().strip()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def is_duplicate(self, title: str, source: str) -> bool:
        """Check if content has been seen before."""
        h = self.compute_hash(title, source)
        return h in self._seen

    def mark_seen(self, title: str, source: str) -> str:
        """Mark content as seen and return its hash."""
        h = self.compute_hash(title, source)
        self._seen.add(h)

        # Evict oldest if at capacity
        if len(self._seen) > self.max_size:
            evict_count = self.max_size // 10
            self._seen = set(list(self._seen)[evict_count:])

        return h

    def get_stats(self) -> dict:
        return {"seen_count": len(self._seen), "capacity": self.max_size}