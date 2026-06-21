"""General helper functions."""
import hashlib
import re
from datetime import datetime
from typing import List, Optional, Set
from config.constants import CRYPTO_SYMBOL_TO_BINANCE


def hash_string(text: str) -> str:
    """Compute a short hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse datetime from various formats."""
    if not value:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a float as a percentage."""
    return f"{value * 100:.{decimals}f}%"


def format_number(value: float, decimals: int = 2) -> str:
    """Format a number with K/M/B suffixes."""
    if abs(value) >= 1e9:
        return f"{value / 1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"{value / 1e3:.{decimals}f}K"
    return f"{value:.{decimals}f}"


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def extract_tickers(text: str, known_tickers: Optional[List[str]] = None) -> List[str]:
    """Extract stock/crypto tickers from text."""
    if known_tickers is None:
        known_tickers = list(CRYPTO_SYMBOL_TO_BINANCE.keys())

    found = set()
    text_upper = text.upper()

    for ticker in known_tickers:
        if re.search(rf"\b{ticker}\b", text_upper):
            found.add(ticker)

    return sorted(found)


def is_crypto_symbol(symbol: str) -> bool:
    """Check if a symbol is a crypto asset."""
    return symbol.upper() in CRYPTO_SYMBOL_TO_BINANCE


def is_forex_symbol(symbol: str) -> bool:
    """Check if a symbol is a forex pair."""
    forex_patterns = [r"^[A-Z]{6}$", r"^[A-Z]{3}/[A-Z]{3}$"]
    for pattern in forex_patterns:
        if re.match(pattern, symbol.upper()) and not is_crypto_symbol(symbol):
            return True
    return False


def symbol_to_binance(symbol: str) -> Optional[str]:
    """Convert a symbol to Binance trading pair."""
    upper = symbol.upper()
    if upper in CRYPTO_SYMBOL_TO_BINANCE:
        return CRYPTO_SYMBOL_TO_BINANCE[upper]
    if upper.endswith("USDT"):
        return upper
    return f"{upper}USDT"


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks."""
    return [lst[i: i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get_nested(data: dict, *keys, default=None):
    """Safely get nested dictionary values."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current