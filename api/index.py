"""Vercel entry point for FastAPI backend."""
import sys
import os

# Add project root to path so imports like config.settings, src.db.* resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.routes import app  # noqa: E402

# Export the ASGI app for Vercel
application = app
