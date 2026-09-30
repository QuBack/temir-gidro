from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .catalog import EQUIPMENT


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
        return ["core:home", "core:catalog", "core:about", "core:contacts", "core:privacy"]

    def location(self, item):
        return reverse(item)


class EquipmentSitemap(CanonicalSitemap):
    def items(self):
        return list(EQUIPMENT)

    def location(self, item):
        return reverse("core:equipment", args=[item])


sitemaps = {"static": StaticViewSitemap, "equipment": EquipmentSitemap}
