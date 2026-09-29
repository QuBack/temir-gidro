import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.utils.html import escape

logger = logging.getLogger(__name__)


def notify_new_lead(lead) -> None:
    """Fire-and-forget: a slow or failing Telegram API must never delay or
    break the visitor's form submission."""
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    threading.Thread(target=_send_telegram, args=(_format(lead),), daemon=True).start()


def _format(lead) -> str:
    lines = [
        "<b>Новая заявка с сайта</b>",
        f"Имя: {escape(lead.name)}",
        f"Телефон: {escape(lead.phone)}",
    ]
    if lead.email:
        lines.append(f"Email: {escape(lead.email)}")
    if lead.message:
        lines.append(f"Комментарий: {escape(lead.message)}")
    if lead.source_page:
        lines.append(f"Страница: {escape(lead.source_page)}")
    if lead.utm_source:
        lines.append(f"Источник: {escape(lead.utm_source)} / {escape(lead.utm_campaign)}")
    return "\n".join(lines)


def _send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    body = json.dumps({"chat_id": settings.TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10):
            pass
    except Exception:
        logger.exception("Telegram notification about a new lead failed")
