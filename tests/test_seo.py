import json
import re

import pytest

from apps.core.templatetags.seo import jsonld

from .conftest import SITE

pytestmark = pytest.mark.django_db


def jsonld_blocks(html: str) -> list[dict]:
    return [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_home_has_core_meta(client):
    html = client.get("/").content.decode()
    assert '<html lang="ru">' in html
    assert f'<link rel="canonical" href="{SITE}/">' in html
    assert html.count("<h1") == 1
    assert "<title>" in html and 'name="description"' in html
    assert 'name="robots"' not in html
    assert f'<meta property="og:url" content="{SITE}/">' in html


def test_canonical_ignores_query_string(client):
    html = client.get("/?utm_source=yandex&utm_medium=cpc").content.decode()
    assert f'<link rel="canonical" href="{SITE}/">' in html


def test_organization_jsonld(client):
    blocks = jsonld_blocks(client.get("/").content.decode())
    org = next(b for b in blocks if b["@type"] == "LocalBusiness")
    assert org["url"] == f"{SITE}/"
    assert org["address"]["@type"] == "PostalAddress"


def test_jsonld_cannot_break_out_of_script():
    rendered = jsonld({"name": "</script><script>alert(1)"})
    assert rendered.count("</script>") == 1


def test_breadcrumbs_visible_and_structured(client):
    html = client.get("/politika-konfidencialnosti/").content.decode()
    assert 'aria-current="page"' in html
    crumbs = next(b for b in jsonld_blocks(html) if b["@type"] == "BreadcrumbList")
    assert [i["item"] for i in crumbs["itemListElement"]] == [f"{SITE}/", f"{SITE}/politika-konfidencialnosti/"]


def test_single_language_has_no_hreflang(client):
    assert "hreflang" not in client.get("/").content.decode()


def test_hreflang_alternates(client, multilingual):
    html = client.get("/").content.decode()
    assert f'hreflang="ru" href="{SITE}/"' in html
    assert f'hreflang="en" href="{SITE}/en/"' in html
    assert f'hreflang="x-default" href="{SITE}/"' in html

    en = client.get("/en/").content.decode()
    assert '<html lang="en">' in en
    assert f'<link rel="canonical" href="{SITE}/en/">' in en


def test_unpublished_language_is_404(client):
    assert client.get("/en/").status_code == 404


def test_robots_txt(client):
    response = client.get("/robots.txt")
    body = response.content.decode()
    assert response["Content-Type"].startswith("text/plain")
    assert f"Sitemap: {SITE}/sitemap.xml" in body
    assert "Clean-param: utm_source" in body
    assert "Disallow: /\n" not in body


def test_staging_closes_indexing(client, settings):
    settings.SEO_INDEXING = False
    assert "Disallow: /\n" in client.get("/robots.txt").content.decode()
    assert '<meta name="robots" content="noindex, nofollow">' in client.get("/").content.decode()


def test_sitemap_uses_canonical_origin(client):
    body = client.get("/sitemap.xml", HTTP_HOST="127.0.0.1").content.decode()
    assert f"<loc>{SITE}/</loc>" in body
    assert f"<loc>{SITE}/politika-konfidencialnosti/</loc>" in body
    assert "127.0.0.1" not in body
    assert "/zayavka/" not in body


def test_sitemap_hreflang(client, multilingual):
    body = client.get("/sitemap.xml").content.decode()
    assert f'hreflang="en" href="{SITE}/en/"' in body
    assert 'hreflang="x-default"' in body


@pytest.mark.parametrize("url", ["/zayavka/", "/zayavka/spasibo/"])
def test_service_pages_are_noindex(client, url):
    html = client.get(url).content.decode()
    assert '<meta name="robots" content="noindex, follow">' in html
    assert 'rel="canonical"' not in html


def test_404_page(client):
    response = client.get("/net-takoj-stranicy/")
    assert response.status_code == 404
    assert 'content="noindex, follow"' in response.content.decode()


def test_missing_trailing_slash_redirects_permanently(client):
    response = client.get("/politika-konfidencialnosti")
    assert response.status_code == 301
    assert response["Location"] == "/politika-konfidencialnosti/"


def test_security_headers(client):
    response = client.get("/")
    assert "default-src 'self'" in response["Content-Security-Policy"]
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
