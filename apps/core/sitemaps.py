import datetime
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.templatetags.static import static
from django.urls import reverse

from .articles import ARTICLES
from .catalog import EQUIPMENT, HERO_IMAGE
from .lift_models import MODELS
from .seo import absolute_url

# Content lives in code, so the sitemap can't know when a page changed. Bump the date of
# the section you edit: Yandex trusts lastmod only while it matches real changes.
STATIC_UPDATED = datetime.date(2026, 10, 2)
EQUIPMENT_UPDATED = datetime.date(2026, 10, 2)
MODELS_UPDATED = datetime.date(2026, 10, 2)


def _image_url(image):
    return absolute_url(static(f"img/{image['src']}-{image['widths'][-1]}.webp"))


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

    def images(self, item):
        """Pictures of the page for the image sitemap (Yandex.Images, Google Images)."""
        return []

    def _urls(self, page, protocol, domain):
        urls = super()._urls(page, protocol, domain)
        for url in urls:
            item = url["item"][0] if self.i18n else url["item"]
            url["images"] = [_image_url(i) for i in self.images(item) if i]
        return urls


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

    def lastmod(self, item):
        return STATIC_UPDATED

    def images(self, item):
        return [HERO_IMAGE] if item == "core:home" else []


class EquipmentSitemap(CanonicalSitemap):
    def items(self):
        return list(EQUIPMENT)

    def location(self, item):
        return reverse("core:equipment", args=[item])

    def lastmod(self, item):
        return EQUIPMENT_UPDATED

    def images(self, item):
        page = EQUIPMENT[item]
        return [page["image"], page.get("about_image"), *(sc["image"] for sc in page.get("scenes", []))]


class ModelSitemap(CanonicalSitemap):
    def items(self):
        return list(MODELS)

    def location(self, item):
        return reverse("core:model", args=item)

    def lastmod(self, item):
        return MODELS_UPDATED

    def images(self, item):
        model = MODELS[item]
        return [*(g["image"] for g in model["images"]), *(sc["image"] for sc in model.get("scenes", []))]


class ArticleSitemap(CanonicalSitemap):
    def items(self):
        return ARTICLES

    def location(self, item):
        return reverse("core:article", args=[item["slug"]])

    def lastmod(self, item):
        return item["date"]

    def images(self, item):
        return [item["image"], *item.get("images", {}).values()]


sitemaps = {
    "static": StaticViewSitemap,
    "equipment": EquipmentSitemap,
    "models": ModelSitemap,
    "articles": ArticleSitemap,
}
