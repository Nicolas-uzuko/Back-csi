import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_smtp(recipient: str, token: str) -> None:
    if not settings.smtp_host:
        logger.warning("Password reset email is not configured; no reset token was logged")
        return
    message = EmailMessage()
    message["Subject"] = "Réinitialisation du mot de passe CSI Sakaraha"
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message.set_content(
        "Une demande de réinitialisation a été effectuée. "
        f"Utilisez ce lien à usage unique : {settings.reset_email_base_url}?token={token}\n"
        "Ce lien expire après une durée limitée. Si vous n'êtes pas à l'origine de la demande, ignorez ce message."
    )
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password or "")
        smtp.send_message(message)


async def send_password_reset_email(recipient: str, token: str) -> None:
    # The clear token only exists in the email body and is never put in the DB/logs/API response.
    await asyncio.to_thread(_send_smtp, recipient, token)
