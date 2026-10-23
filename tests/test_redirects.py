from urllib.parse import quote

import pytest

from apps.core.redirects import OLD_TO_NEW

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("old,new", sorted(OLD_TO_NEW.items()))
def test_old_site_address_redirects_permanently_to_a_live_page(client, old, new):
    response = client.get(quote(old + "/"))
    assert response.status_code == 301 and response["Location"] == new
    assert client.get(new).status_code == 200


def test_redirect_without_slash_and_with_utm(client):
    response = client.get("/equipment/temir-gidro-1x?utm_source=yandex")
    assert response.status_code == 301
    assert response["Location"] == "/podemniki/nozhnichnye/1x/?utm_source=yandex"


def test_new_pages_are_not_redirected(client):
    assert client.get("/podemniki/nozhnichnye/1x/").status_code == 200
