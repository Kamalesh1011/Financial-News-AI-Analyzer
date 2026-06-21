"""Telegram Bot for sending alerts."""
from typing import Optional
from loguru import logger
import httpx

from config.settings import settings


class TelegramBot:
    """Telegram Bot API client for sending alerts."""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.http_client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None

    async def send_message(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: Optional[str] = "Markdown",
        disable_preview: bool = True,
    ) -> bool:
        """Send a text message to Telegram."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured")
            return False

        await self.initialize()

        target_chat = chat_id or self.chat_id

        try:
            response = await self.http_client.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": target_chat,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": disable_preview,
                },
            )
            response.raise_for_status()
            data = response.json()

            if data.get("ok"):
                logger.info(f"Telegram message sent to {target_chat}")
                return True
            else:
                logger.error(f"Telegram API error: {data}")
                return False

        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False

    async def send_photo(
        self,
        photo_url: str,
        caption: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> bool:
        """Send a photo to Telegram."""
        if not self.bot_token or not self.chat_id:
            return False

        await self.initialize()

        target_chat = chat_id or self.chat_id

        try:
            payload = {
                "chat_id": target_chat,
                "photo": photo_url,
            }
            if caption:
                payload["caption"] = caption

            response = await self.http_client.post(
                f"{self.base_url}/sendPhoto",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("ok", False)

        except Exception as e:
            logger.error(f"Telegram photo send failed: {e}")
            return False

    async def get_me(self) -> Optional[dict]:
        """Get bot information."""
        if not self.bot_token:
            return None

        await self.initialize()

        try:
            response = await self.http_client.get(f"{self.base_url}/getMe")
            response.raise_for_status()
            data = response.json()
            return data.get("result")
        except Exception as e:
            logger.error(f"Telegram getMe failed: {e}")
            return None