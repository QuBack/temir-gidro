import pytest

from .conftest import SITE
from .test_seo import jsonld_blocks

pytestmark = pytest.mark.django_db


def test_contacts_page(client):
    response = client.get("/kontakty/")
    html = response.content.decode()
    assert response.status_code == 200
    assert html.count("<h1") == 1
    assert 'href="tel:+74991170131"' in html
    assert "data-lead-form" in html
    crumbs = next(b for b in jsonld_blocks(html) if b["@type"] == "BreadcrumbList")
    assert crumbs["itemListElement"][-1]["item"] == f"{SITE}/kontakty/"


def test_contacts_map_is_embedded_lazily(client):
    html = client.get("/kontakty/").content.decode()
    assert 'src="https://yandex.ru/map-widget/v1/?text=' in html
    assert 'loading="lazy"' in html
    assert "overlay" not in html.split("<main")[0].split("<body")[1]  # plain white header


def test_lead_page_has_photo_and_form(client):
    html = client.get("/zayavka/").content.decode()
    assert "hero/gidravlicheskie-podemniki" in html
    assert "data-lead-form" in html
    assert 'class="overlay overlay--dark"' in html


def test_menu(client):
    html = client.get("/").content.decode()
    assert "/proekty/" not in html
    assert 'href="/podemniki/nozhnichnye/3x/"' in html
    assert "Оставить заявку" in html


def test_series_anchors_exist(client):
    html = client.get("/podemniki/nozhnichnye/").content.decode()
    for name in ("1x", "2x", "3x", "4x"):
        assert f'id="seriya-{name}"' in html


def test_about_page(client):
    response = client.get("/o-kompanii/")
    html = response.content.decode()
    assert response.status_code == 200
    assert html.count("<h1") == 1
    types = {b["@type"] for b in jsonld_blocks(html)}
    assert {"LocalBusiness", "BreadcrumbList", "AboutPage"} <= types
    assert f"<loc>{SITE}/o-kompanii/</loc>" in client.get("/sitemap.xml").content.decode()


def test_no_template_comments_leak(client):
    # {# #} is single-line only: a multi-line one is printed as text.
    for url in ("/", "/podemniki/", "/podemniki/nozhnichnye/", "/podemniki/nozhnichnye/1x/"):
        assert "{#" not in client.get(url).content.decode()


def test_contacts_and_social(client):
    html = client.get("/kontakty/").content.decode()
    assert 'href="tel:+74991170131"' in html and 'href="tel:+79300129592"' in html
    assert "https://vk.ru/temir_gidro" in html and "https://www.youtube.com/@temir-gidro" in html
    assert "https://www.instagram.com/temirgidro/" in html
    assert "8 (800)" not in html


def test_scene_photos_open_full_screen(client):
    html = client.get("/podemniki/dlya-okrasochnyh-kamer/1x/").content.decode()
    assert 'data-zoom="scenes"' in html and "data-lightbox" in html and "js/lightbox.js" in html


def test_home_steps_timeline(client):
    html = client.get("/").content.decode()
    # Five steps, each with a photo; the content is in the HTML, JS only animates it.
    assert html.count('class="timeline__item" data-reveal') == 5
    assert "img/steps/etap-montazh-1536.webp" in html
