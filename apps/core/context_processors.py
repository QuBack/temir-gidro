from django.conf import settings
from django.urls import translate_url

from .company import COMPANY
from .seo import absolute_url


def site(request):
    path = request.path
    alternates = []
    if len(settings.LANGUAGES) > 1:
        alternates = [
            {"code": code, "name": name, "url": absolute_url(translate_url(path, code))}
            for code, name in settings.LANGUAGES
        ]
    return {
        "company": COMPANY,
        # Query strings (utm, filters) are never part of the canonical URL.
        "canonical_url": absolute_url(path),
        "alternates": alternates,
        "x_default_url": absolute_url(translate_url(path, settings.LANGUAGE_CODE)),
        "seo_indexing": settings.SEO_INDEXING,
        "yandex_verification": settings.YANDEX_VERIFICATION,
        "google_verification": settings.GOOGLE_VERIFICATION,
        "yandex_metrika_id": settings.YANDEX_METRIKA_ID,
    }
