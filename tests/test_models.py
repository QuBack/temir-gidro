import pytest

from .conftest import SITE
from .test_seo import jsonld_blocks

pytestmark = pytest.mark.django_db

URL = "/podemniki/nozhnichnye/1x/"


@pytest.mark.parametrize(
    "path", ["nozhnichnye/1x", "nozhnichnye/2x", "nozhnichnye/3x", "nozhnichnye/4x",
             "dlya-okrasochnyh-kamer/1x", "dlya-okrasochnyh-kamer/2d"]
)
def test_model_pages_render(client, path):
    response = client.get(f"/podemniki/{path}/")
    html = response.content.decode()
    assert response.status_code == 200
    assert html.count("<h1") == 1
    assert 'id="zayavka"' in html and "data-lead-form" in html
    assert 'id="komplektaciya"' in html and 'id="postavka"' in html


def test_model_page_is_not_a_shop(client):
    html = client.get(URL).content.decode()
    assert "корзин" not in html.lower()
    assert "Количество:" not in html
    assert "Оставить заявку" in html


def test_model_jsonld(client):
    blocks = jsonld_blocks(client.get(URL).content.decode())
    types = {b["@type"] for b in blocks}
    assert {"LocalBusiness", "BreadcrumbList", "Product", "FAQPage"} <= types
    product = next(b for b in blocks if b["@type"] == "Product")
    assert product["url"] == f"{SITE}{URL}"
    assert product["model"] == "1X"
    # Unconfirmed specs are not published as data.
    assert all(p["value"] for p in product["additionalProperty"])
    crumbs = next(b for b in blocks if b["@type"] == "BreadcrumbList")
    assert [i["item"] for i in crumbs["itemListElement"]] == [
        f"{SITE}/",
        f"{SITE}/podemniki/",
        f"{SITE}/podemniki/nozhnichnye/",
        f"{SITE}{URL}",
    ]


def test_kit_markers_on_picture(client):
    html = client.get(URL).content.decode()
    assert 'class="kit__overlay"' in html
    assert 'data-kit-marker="1"' in html
    assert "style=" not in html.split('id="komplektaciya"')[1].split("</section>")[0]  # CSP: no inline styles


def test_unknown_model_is_404(client):
    assert client.get("/podemniki/nozhnichnye/9x/").status_code == 404
    assert client.get("/podemniki/net-takogo/1x/").status_code == 404


def test_models_in_sitemap(client):
    assert f"<loc>{SITE}{URL}</loc>" in client.get("/sitemap.xml").content.decode()


def test_line_page_links_to_models(client):
    html = client.get("/podemniki/nozhnichnye/").content.decode()
    for slug in ("1x", "2x", "3x", "4x"):
        assert f'href="/podemniki/nozhnichnye/{slug}/"' in html


def test_scissor_specs_from_old_site(client):
    html = client.get("/podemniki/nozhnichnye/3x/").content.decode()
    assert "2350–16 000" in html and "2700–17 500" in html
    # Specs the client never published are left out, not shown as «уточняется».
    assert "уточняется" not in client.get("/podemniki/nozhnichnye/2x/").content.decode()
    assert "1500–10 600" in client.get("/podemniki/nozhnichnye/2x/").content.decode()
