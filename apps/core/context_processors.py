from django.conf import settings
from django.templatetags.static import static
from django.urls import translate_url

from .catalog import CATEGORIES, CONFIG_BG, LEAD_BG, SPECS_BG
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
        "nav_categories": CATEGORIES,
        "lead_bg": LEAD_BG,
        "config_bg": CONFIG_BG,
        "specs_bg": SPECS_BG,
        # Query strings (utm, filters) are never part of the canonical URL.
        "canonical_url": absolute_url(path),
        # Link previews in messengers and social networks when a page sets no og_image.
        "default_og_image": absolute_url(static("img/og/temir-gidro-1200x630.jpg")),
        "alternates": alternates,
        "x_default_url": absolute_url(translate_url(path, settings.LANGUAGE_CODE)),
        "seo_indexing": settings.SEO_INDEXING,
        "yandex_verification": settings.YANDEX_VERIFICATION,
        "google_verification": settings.GOOGLE_VERIFICATION,
        "yandex_metrika_id": settings.YANDEX_METRIKA_ID,
    }
