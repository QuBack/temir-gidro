import pytest

from .conftest import SITE
from .test_seo import jsonld_blocks

pytestmark = pytest.mark.django_db

URL = "/podemniki/nozhnichnye/"


def test_equipment_page_renders(client):
    response = client.get(URL)
    html = response.content.decode()
    assert response.status_code == 200
    assert html.count("<h1") == 1
    assert f'<link rel="canonical" href="{SITE}{URL}">' in html
    assert 'id="raschet"' in html and "data-lead-form" in html


def test_equipment_jsonld(client):
    blocks = jsonld_blocks(client.get(URL).content.decode())
    types = {b["@type"] for b in blocks}
    assert {"LocalBusiness", "BreadcrumbList", "Product", "FAQPage"} <= types
    product = next(b for b in blocks if b["@type"] == "Product")
    assert product["url"] == f"{SITE}{URL}"
    assert product["manufacturer"]["@id"] == f"{SITE}/#organization"
    crumbs = next(b for b in blocks if b["@type"] == "BreadcrumbList")
    assert crumbs["itemListElement"][-1]["item"] == f"{SITE}{URL}"


def test_unknown_equipment_is_404(client):
    assert client.get("/podemniki/net-takogo/").status_code == 404


def test_equipment_in_sitemap(client):
    assert f"<loc>{SITE}{URL}</loc>" in client.get("/sitemap.xml").content.decode()


def test_painting_booth_page(client):
    html = client.get("/podemniki/dlya-okrasochnyh-kamer/").content.decode()
    assert html.count("<h1") == 1
    assert 'id="seriya-1x"' in html and 'id="seriya-2d"' in html
    assert 'href="/podemniki/dlya-okrasochnyh-kamer/2d/"' in html


@pytest.mark.parametrize("slug", ["chetyrehstoechnye", "avtomobilnye"])
def test_lines_without_models(client, slug):
    html = client.get(f"/podemniki/{slug}/").content.decode()
    assert html.count("<h1") == 1
    assert 'id="serii"' not in html  # no serial models yet
    assert 'aria-labelledby="about-title"' in html and "photos/" in html


def test_equipment_breadcrumbs_include_section(client):
    crumbs = next(b for b in jsonld_blocks(client.get(URL).content.decode()) if b["@type"] == "BreadcrumbList")
    assert [i["item"] for i in crumbs["itemListElement"]] == [f"{SITE}/", f"{SITE}/podemniki/", f"{SITE}{URL}"]


def test_catalog_section(client):
    html = client.get("/podemniki/").content.decode()
    assert html.count("<h1") == 1
    collection = next(b for b in jsonld_blocks(html) if b["@type"] == "CollectionPage")
    urls = [i["url"] for i in collection["mainEntity"]["itemListElement"]]
    assert f"{SITE}/podemniki/nozhnichnye/" in urls and len(urls) == 6
    assert f"<loc>{SITE}/podemniki/</loc>" in client.get("/sitemap.xml").content.decode()
