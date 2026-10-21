import pytest

from .conftest import SITE
from .test_seo import jsonld_blocks

pytestmark = pytest.mark.django_db


def test_cylinders_page(client):
    response = client.get("/gidrocilindry/")
    html = response.content.decode()
    assert response.status_code == 200
    assert html.count("<h1") == 1
    types = {b["@type"] for b in jsonld_blocks(html)}
    assert {"Product", "FAQPage", "BreadcrumbList"} <= types


def test_cylinder_configurator(client):
    """The configurator gets the catalog tables as JSON and links the catalog PDF that is in static/."""
    import json
    import re

    from django.contrib.staticfiles import finders

    html = client.get("/gidrocilindry/").content.decode()
    assert "data-cyl-config" in html
    found = re.search(r'<script id="cyl-config-data" type="application/json">(.*?)</script>', html, re.S)
    data = json.loads(found.group(1))
    assert set(data["mounts"]) == {"MF3", "MF4", "MP3", "MP5", "MT4", "MS2"}
    for mount in data["mounts"].values():
        assert len(mount["A"]) == len(data["bores"])
    assert finders.find("docs/katalog-gidrocilindrov-temir-gidro.pdf")
    assert "katalog-gidrocilindrov-temir-gidro.pdf" in html


def test_power_units_page(client):
    """The page renders with its calculator data, links the questionnaire PDF and is in the menu."""
    from django.contrib.staticfiles import finders

    html = client.get("/gidrostancii/").content.decode()
    assert html.count("<h1") == 1
    types = {b["@type"] for b in jsonld_blocks(html)}
    assert {"Product", "FAQPage", "BreadcrumbList"} <= types
    assert 'id="pu-config-data"' in html
    assert finders.find("docs/oprosnyj-list-gidrostanciya-temir-gidro.pdf")
    assert "oprosnyj-list-gidrostanciya-temir-gidro.pdf" in html
    assert 'href="/gidrostancii/"' in client.get("/").content.decode()


def test_article_list(client):
    html = client.get("/stati/").content.decode()
    assert html.count("<h1") == 1
    assert 'href="/stati/nozhnichnyj-podemnik-dlya-avtoservisa/"' in html


@pytest.mark.parametrize(
    "slug",
    [
        "nozhnichnyj-podemnik-dlya-avtoservisa",
        "kak-vybrat-nozhnichnyj-podemnik",
        "podzemnye-kontejnernye-ploshchadki",
        "svarnoj-ili-razbornyj-gidrocilindr",
    ],
)
def test_article_pages(client, slug):
    response = client.get(f"/stati/{slug}/")
    html = response.content.decode()
    assert response.status_code == 200
    assert html.count("<h1") == 1
    post = next(b for b in jsonld_blocks(html) if b["@type"] == "BlogPosting")
    assert post["url"] == f"{SITE}/stati/{slug}/"
    assert '<meta property="og:type" content="article">' in html


def test_unknown_article_is_404(client):
    assert client.get("/stati/net-takoj/").status_code == 404


def test_new_pages_in_sitemap(client):
    xml = client.get("/sitemap.xml").content.decode()
    for path in ("/gidrocilindry/", "/stati/", "/stati/kak-vybrat-nozhnichnyj-podemnik/",
                 "/podemniki/dlya-musornyh-kontejnerov/"):
        assert f"<loc>{SITE}{path}</loc>" in xml


def test_waste_container_page(client):
    html = client.get("/podemniki/dlya-musornyh-kontejnerov/").content.decode()
    assert html.count("<h1") == 1
    assert "Технические характеристики" in html and "Стандартная комплектация" in html
