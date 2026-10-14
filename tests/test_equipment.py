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
    # The scissor page lists its models: a collection, not a product without an offer.
    assert {"LocalBusiness", "BreadcrumbList", "CollectionPage", "FAQPage"} <= types
    assert "Product" not in types
    collection = next(b for b in blocks if b["@type"] == "CollectionPage")
    assert collection["url"] == f"{SITE}{URL}"
    urls = [i["url"] for i in collection["mainEntity"]["itemListElement"]]
    assert urls == [f"{SITE}{URL}{m}/" for m in ("1x", "2x", "3x", "4x")]
    crumbs = next(b for b in blocks if b["@type"] == "BreadcrumbList")
    assert crumbs["itemListElement"][-1]["item"] == f"{SITE}{URL}"


def test_line_without_showcase_is_a_product(client):
    types = {b["@type"] for b in jsonld_blocks(client.get("/podemniki/dlya-okrasochnyh-kamer/").content.decode())}
    assert "Product" in types and "CollectionPage" not in types


def test_scissor_showcase(client):
    html = client.get(URL).content.decode()
    for m in ("1x", "2x", "3x", "4x"):
        assert f'id="seriya-{m}"' in html and f'href="{URL}{m}/"' in html
    assert html.count("<h2") >= 4 and "Ножничный подъёмник 4X</h2>" in html
    assert 'id="sravnenie"' in html and '<table class="compare">' in html and "до 20 000" in html
    assert 'id="dlya-rascheta"' in html
    # The configurator closes the page, right above the request form.
    assert html.index('id="podbor"') > html.index('aria-labelledby="related-title"')
    assert html.index('id="podbor"') < html.index('id="raschet"')


def test_unknown_equipment_is_404(client):
    assert client.get("/podemniki/net-takogo/").status_code == 404


def test_equipment_in_sitemap(client):
    assert f"<loc>{SITE}{URL}</loc>" in client.get("/sitemap.xml").content.decode()


def test_painting_booth_page(client):
    html = client.get("/podemniki/dlya-okrasochnyh-kamer/").content.decode()
    assert html.count("<h1") == 1
    assert 'id="seriya-1x"' in html and 'id="seriya-2d"' in html and 'id="seriya-3d"' in html
    assert 'href="/podemniki/dlya-okrasochnyh-kamer/2d/"' in html
    assert 'href="/podemniki/dlya-okrasochnyh-kamer/3d/"' in html


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


def test_console_lift_page(client):
    html = client.get("/podemniki/konsolnye/").content.decode()
    assert "Консольные подъёмники" in html
    assert "1500–12 000" in html
    assert f"<loc>{SITE}/podemniki/konsolnye/</loc>" in client.get("/sitemap.xml").content.decode()


def test_configurator_uses_client_tables(client):
    html = client.get(URL).content.decode()
    # Sliders stop where the client's tables end: 5.5 m and 5.5 t.
    assert 'name="L" min="1200" max="5500"' in html and 'name="Q" min="0.5" max="5.5"' in html
    assert 'data-out="Hmin"' in html and 'data-out="D"' in html and "data-config-note" in html
