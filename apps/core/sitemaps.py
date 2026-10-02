from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .articles import ARTICLES
from .catalog import EQUIPMENT
from .lift_models import MODELS


class CanonicalSitemap(Sitemap):
    """Every URL in the sitemap uses SITE_URL, regardless of the request host.
    Emits hreflang alternates for every published language."""

    i18n = True
    alternates = True
    x_default = True

    def get_domain(self, site=None):
        return urlsplit(settings.SITE_URL).netloc

    def get_protocol(self, protocol=None):
        return urlsplit(settings.SITE_URL).scheme


class StaticViewSitemap(CanonicalSitemap):
    def items(self):
        return [
            "core:home",
            "core:catalog",
            "core:cylinders",
            "core:articles",
            "core:about",
            "core:contacts",
            "core:privacy",
        ]

    def location(self, item):
        return reverse(item)


class EquipmentSitemap(CanonicalSitemap):
    def items(self):
        return list(EQUIPMENT)

    def location(self, item):
        return reverse("core:equipment", args=[item])


class ModelSitemap(CanonicalSitemap):
    def items(self):
        return list(MODELS)

    def location(self, item):
        return reverse("core:model", args=item)


class ArticleSitemap(CanonicalSitemap):
    def items(self):
        return ARTICLES

    def location(self, item):
        return reverse("core:article", args=[item["slug"]])

    def lastmod(self, item):
        return item["date"]


sitemaps = {
    "static": StaticViewSitemap,
    "equipment": EquipmentSitemap,
    "models": ModelSitemap,
    "articles": ArticleSitemap,
}
