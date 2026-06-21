"""Email sender for alerts via SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger

from config.settings import settings


class EmailSender:
    """Email sender using SMTP."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_pass = settings.smtp_pass

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send an email."""
        if not self.smtp_user or not self.smtp_pass:
            logger.warning("SMTP not configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to_email

            if text_body:
                msg.attach(MIMEText(text_body, "plain"))

            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def send_alert_email(
        self,
        to_email: str,
        subject: str,
        markdown_content: str,
    ) -> bool:
        """Send a formatted alert email."""
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                .alert-box {{ background: white; border-left: 4px solid #667eea; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 10px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin:0;">Financial News Alert</h1>
                </div>
                <div class="content">
                    <div class="alert-box">
                        {markdown_content.replace(chr(10), '<br>')}
                    </div>
                </div>
                <div class="footer">
                    <p>Financial News AI Analyzer</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"Financial News Alert\n\n{markdown_content}"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

    async def cleanup(self) -> None:
        """Cleanup resources."""
        pass