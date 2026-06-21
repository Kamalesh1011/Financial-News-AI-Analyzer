"""Tests for FastAPI API endpoints."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


@pytest.fixture
def mock_settings():
    """Mock settings for tests."""
    with patch("config.settings.Settings") as mock:
        mock_instance = mock.return_value
        mock_instance.jwt_secret = "test-secret"
        mock_instance.jwt_algorithm = "HS256"
        mock_instance.jwt_expire_minutes = 60
        yield mock_instance


def test_hash_password():
    """Test password hashing."""
    from src.api.auth import hash_password, verify_password
    pwd = "testpassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT token creation."""
    from src.api.auth import create_access_token
    data = {"sub": "user123", "username": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """Test valid token verification."""
    from src.api.auth import create_access_token, verify_token
    data = {"sub": "user123", "username": "testuser"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["sub"] == "user123"
    assert payload["username"] == "testuser"


def test_verify_token_invalid():
    """Test invalid token raises error."""
    from src.api.auth import verify_token
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid.token.here")
    assert exc_info.value.status_code == 401


def test_serialize_doc():
    """Test _serialize_doc helper."""
    from src.api.routes import _serialize_doc
    doc = {
        "_id": MagicMock(__str__=lambda self: "abc123"),
        "created_at": datetime(2024, 1, 15, 12, 0, 0),
        "name": "test",
    }
    result = _serialize_doc(doc)
    assert result["_id"] == "abc123"
    assert result["created_at"] == "2024-01-15T12:00:00"
    assert result["name"] == "test"
