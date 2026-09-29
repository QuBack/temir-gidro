from django.conf import settings
from django.core.cache import cache

UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")
SOURCE_SESSION_KEY = "lead_source"


def get_client_ip(request) -> str | None:
    if settings.USE_X_FORWARDED_FOR:
        # The reverse proxy appends the real client address as the last entry.
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[-1].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def is_rate_limited(ip: str | None) -> bool:
    """Counts submissions per IP in a fixed window; True once the limit is exceeded."""
    if not ip:
        return False
    key = f"lead-rate:{ip}"
    cache.add(key, 0, timeout=settings.LEAD_RATE_WINDOW)
    try:
        count = cache.incr(key)
    except ValueError:  # expired between add() and incr()
        cache.set(key, 1, timeout=settings.LEAD_RATE_WINDOW)
        count = 1
    return count > settings.LEAD_RATE_LIMIT
