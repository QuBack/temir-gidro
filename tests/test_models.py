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


def test_model_page_tabs_and_full_name_in_crumbs(client):
    html = client.get("/podemniki/nozhnichnye/1x/").content.decode()
    assert html.count("data-tab-panel") == 4 and "js/tabs.js" in html
    for panel in ("opisanie", "harakteristiki", "komplektaciya", "postavka"):
        assert f'href="#{panel}" data-tab' in html and f'id="{panel}"' in html
    crumbs = html[html.index('class="breadcrumbs'):]
    assert "Ножничный подъёмник 1X" in crumbs[: crumbs.index("</nav>")]


def test_model_has_one_picture_on_first_screen(client):
    html = client.get("/podemniki/dlya-okrasochnyh-kamer/2d/").content.decode()
    hero = html[: html.index('class="tabs"')]
    assert hero.count('data-zoom="views"') == 1
    # The other two views sit under the description, in the same viewer group.
    assert html.count('class="model-views__item zoom"') == 2


@pytest.mark.parametrize("slug", ["1x", "2x"])
def test_scissor_model_has_3d_viewer(client, slug):
    html = client.get(f"/podemniki/nozhnichnye/{slug}/").content.decode()
    glb = f'data-model3d="/static/models/nozhnichnyj-podemnik-{slug}.glb"'
    hero = html[: html.index('class="tabs"')]
    assert "data-model3d" not in hero  # the first screen keeps just the render
    assert html.count(glb) == 1 and 'id="3d" hidden' in html  # the block, shown by JS
    assert 'src="/static/js/model3d.js"' in html and 'data-draco="/static/vendor/draco/"' in html


def test_model_without_3d_has_no_viewer(client):
    html = client.get("/podemniki/nozhnichnye/3x/").content.decode()
    assert "data-model3d" not in html and "model3d.js" not in html


def test_3d_files_are_served_from_our_static():
    from django.contrib.staticfiles import finders

    for path in ("models/nozhnichnyj-podemnik-1x.glb", "models/nozhnichnyj-podemnik-2x.glb",
                 "vendor/model-viewer/model-viewer.min.js", "vendor/draco/draco_decoder.wasm",
                 "vendor/draco/draco_wasm_wrapper.js", "js/model3d.js"):
        assert finders.find(path), path


def test_csp_allows_the_3d_viewer_and_nothing_wider(client, settings):
    csp = client.get("/podemniki/nozhnichnye/1x/")["Content-Security-Policy"]
    assert "'wasm-unsafe-eval'" in csp and "worker-src 'self' blob:" in csp
    assert "'unsafe-inline'" not in csp and "'unsafe-eval'" not in csp
    assert settings.MODEL_VIEWER_STYLE_HASH in csp


def test_model_viewer_style_hash_matches_vendored_file(settings):
    """The viewer styles its shadow DOM with one <style> block; CSP allows exactly that block."""
    import base64
    import hashlib
    import re

    from django.contrib.staticfiles import finders

    source = open(finders.find("vendor/model-viewer/model-viewer.min.js"), encoding="utf-8").read()
    style = re.search(r"<style>(\n:host \{.*?)</style>", source, re.S).group(1)
    digest = base64.b64encode(hashlib.sha256(style.encode()).digest()).decode()
    assert settings.MODEL_VIEWER_STYLE_HASH == f"'sha256-{digest}'"
