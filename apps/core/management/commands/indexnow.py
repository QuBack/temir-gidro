"""Tell Yandex and Bing which pages changed: python manage.py indexnow [path …]

Without arguments sends every URL of the sitemap — run it after a deploy that changed
content. Does nothing until INDEXNOW_KEY is set.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.core.management.base import BaseCommand, CommandError

from apps.core.seo import absolute_url
from apps.core.sitemaps import sitemaps

ENDPOINT = "https://yandex.com/indexnow"  # shared with Bing and the other IndexNow engines


class Command(BaseCommand):
    help = "Submit changed URLs to IndexNow (Yandex, Bing)."

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="*", help="Site paths, e.g. /podemniki/nozhnichnye/. Default: the sitemap.")

    def handle(self, *args, paths, **options):
        key = settings.INDEXNOW_KEY
        if not key:
            self.stdout.write("INDEXNOW_KEY is not set: nothing sent.")
            return
        if not settings.SEO_INDEXING:
            self.stdout.write("SEO_INDEXING is off (staging): nothing sent.")
            return
        urls = [absolute_url(p) for p in paths] or self.sitemap_urls()
        host = absolute_url("/").split("/")[2]
        payload = {"host": host, "key": key, "keyLocation": absolute_url(f"/{key}.txt"), "urlList": urls}
        request = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            raise CommandError(f"IndexNow answered {error.code}: {error.read()[:300]!r}") from error
        self.stdout.write(f"IndexNow: {len(urls)} URL(s) sent, answer {status}.")

    @staticmethod
    def sitemap_urls():
        urls = []
        for cls in sitemaps.values():
            site_map: Sitemap = cls()
            urls += [u["location"] for u in site_map.get_urls(protocol=None, site=None)]
        return urls
