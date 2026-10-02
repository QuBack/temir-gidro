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
