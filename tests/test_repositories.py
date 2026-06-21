"""Tests for MongoDB repositories."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB instance."""
    with patch("src.db.repositories.MongoDB") as mock:
        mock_instance = mock.return_value
        mock_collection = AsyncMock()
        mock_instance.collection.return_value = mock_collection
        yield mock_instance, mock_collection


def test_sentiment_trend_aggregation():
    """Test sentiment trend pipeline structure."""
    from src.db.repositories import SentimentRepository
    repo = SentimentRepository()
    # Verify the repository can be instantiated
    assert repo is not None
    assert hasattr(repo, "get_sentiment_trend")


def test_source_credibility_structure():
    """Test source credibility method exists."""
    from src.db.repositories import SentimentRepository
    repo = SentimentRepository()
    assert hasattr(repo, "get_source_credibility")


def test_market_data_price_history():
    """Test price history method exists."""
    from src.db.repositories import MarketDataRepository
    repo = MarketDataRepository()
    assert hasattr(repo, "get_price_history")


def test_market_data_correlation():
    """Test correlation matrix method exists."""
    from src.db.repositories import MarketDataRepository
    repo = MarketDataRepository()
    assert hasattr(repo, "get_correlation_matrix")


def test_user_repository():
    """Test UserRepository exists with expected methods."""
    from src.db.repositories import UserRepository
    repo = UserRepository()
    assert hasattr(repo, "create_user")
    assert hasattr(repo, "get_by_username")
    assert hasattr(repo, "get_by_email")


def test_watchlist_repository():
    """Test WatchlistRepository methods."""
    from src.db.repositories import WatchlistRepository
    repo = WatchlistRepository()
    assert hasattr(repo, "get_user_watchlist")
    assert hasattr(repo, "add_to_watchlist")
    assert hasattr(repo, "remove_from_watchlist")


def test_job_run_repository():
    """Test JobRunRepository methods."""
    from src.db.repositories import JobRunRepository
    repo = JobRunRepository()
    assert hasattr(repo, "log_run")
    assert hasattr(repo, "get_recent_runs")
