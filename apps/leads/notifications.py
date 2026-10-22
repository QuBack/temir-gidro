import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.html import escape

logger = logging.getLogger(__name__)


def notify_new_lead(lead) -> None:
    """Fire-and-forget: a slow or failing Telegram API or mail server must never delay or
    break the visitor's form submission. The lead itself is already in the admin."""
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        threading.Thread(target=_send_telegram, args=(_format(lead),), daemon=True).start()
    if settings.EMAIL_HOST and settings.EMAIL_HOST_PASSWORD and settings.LEAD_NOTIFY_EMAILS:
        message = _email(lead)  # built here: the thread must not touch the database
        threading.Thread(target=_send_email, args=(message,), daemon=True).start()


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


def _email(lead) -> EmailMessage:
    """Plain text, the same fields as the Telegram message plus a link to the lead in the admin.
    «Ответить» in the mail client answers the visitor when they left an email."""
    lines = [f"Имя: {lead.name}", f"Телефон: {lead.phone}"]
    if lead.email:
        lines.append(f"Email: {lead.email}")
    if lead.message:
        lines += ["", "Комментарий:", lead.message, ""]
    if lead.source_page:
        lines.append(f"Страница: {lead.source_page}")
    if lead.utm_source:
        lines.append(f"Источник: {lead.utm_source} / {lead.utm_campaign}")
    admin = settings.SITE_URL.rstrip("/") + reverse("admin:leads_lead_change", args=[lead.pk])
    lines += ["", f"Заявка в админке: {admin}"]
    return EmailMessage(
        subject=f"Заявка с сайта: {lead.name}, {lead.phone}",
        body="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.LEAD_NOTIFY_EMAILS,
        reply_to=[lead.email] if lead.email else None,
    )


def _send_email(message: EmailMessage) -> None:
    try:
        message.send()
    except Exception:
        logger.exception("Email notification about a new lead failed")
