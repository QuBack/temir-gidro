from urllib.parse import urlsplit

from django.conf import settings

from .utils import SOURCE_SESSION_KEY, UTM_FIELDS


class UtmCaptureMiddleware:
    """Remembers the first-touch traffic source (UTM tags, external referrer,
    landing page) in the session so it can be attached to a lead later."""

    CLICK_IDS = ("yclid", "gclid")

    def __init__(self, get_response):
        self.get_response = get_response
        self.own_host = urlsplit(settings.SITE_URL).netloc

    def __call__(self, request):
        if request.method == "GET" and not request.path.startswith(("/static/", "/media/")):
            self.capture(request)
        return self.get_response(request)

    def capture(self, request):
        utm = {f: request.GET[f][:200] for f in UTM_FIELDS if request.GET.get(f)}
        has_click_id = any(request.GET.get(p) for p in self.CLICK_IDS)
        referrer = request.META.get("HTTP_REFERER", "")[:500]
        external_referrer = bool(referrer) and urlsplit(referrer).netloc not in (self.own_host, request.get_host())

        if not (utm or has_click_id or external_referrer):
            return
        if SOURCE_SESSION_KEY in request.session:
            return  # first touch wins
        request.session[SOURCE_SESSION_KEY] = {
            **utm,
            "referrer": referrer if external_referrer else "",
            "landing_page": request.get_full_path()[:500],
        }
