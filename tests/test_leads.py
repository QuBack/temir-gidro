import time
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core import signing

from apps.leads.forms import _TOKEN_SALT
from apps.leads.models import Lead

pytestmark = pytest.mark.django_db


def test_form_submission_without_js(client, lead_data, django_capture_on_commit_callbacks):
    with mock.patch("apps.leads.views.notify_new_lead") as notify:
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post("/zayavka/", lead_data)

    assert response.status_code == 302
    assert response["Location"] == "/zayavka/spasibo/"
    lead = Lead.objects.get()
    assert lead.status == Lead.Status.NEW
    assert lead.phone == "+77001234567"
    assert lead.source_page == "/"
    assert lead.language == "ru"
    notify.assert_called_once_with(lead)


def test_form_submission_json(client, lead_data):
    response = client.post("/zayavka/", lead_data, HTTP_ACCEPT="application/json")
    assert response.json() == {"ok": True}
    assert Lead.objects.count() == 1


def test_invalid_submission_returns_errors(client, lead_data):
    lead_data.update(phone="123", consent="")
    response = client.post("/zayavka/", lead_data, HTTP_ACCEPT="application/json")
    assert response.status_code == 400
    assert set(response.json()["errors"]) == {"phone", "consent"}
    assert not Lead.objects.exists()


def test_invalid_submission_without_js_rerenders_form(client, lead_data):
    lead_data["name"] = ""
    response = client.post("/zayavka/", lead_data)
    assert response.status_code == 400
    assert 'class="errorlist' in response.content.decode()


@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"website": "http://spam.example"}, "honeypot"),
        ({"token": "forged"}, "bad_token"),
        # Token ages as callables: parametrize runs at collection, seconds before the test.
        ({"token": lambda: signing.dumps(int(time.time()), salt=_TOKEN_SALT)}, "too_fast"),
        ({"token": lambda: signing.dumps(int(time.time()) - 8 * 24 * 3600, salt=_TOKEN_SALT)}, "stale_token"),
        ({"name": "Buy now https://spam.example"}, "links"),
        ({"message": "http://a.example and www.b.example"}, "links"),
    ],
)
def test_spam_is_kept_silently_and_not_announced(
    client, lead_data, override, reason, django_capture_on_commit_callbacks
):
    lead_data.update({k: v() if callable(v) else v for k, v in override.items()})
    with mock.patch("apps.leads.views.notify_new_lead") as notify:
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post("/zayavka/", lead_data)

    assert response.status_code == 302  # the bot sees the same success
    lead = Lead.objects.get()
    assert (lead.status, lead.spam_reason) == (Lead.Status.SPAM, reason)
    notify.assert_not_called()


def test_rate_limit(client, lead_data, settings):
    settings.LEAD_RATE_LIMIT = 2
    for _ in range(2):
        assert client.post("/zayavka/", lead_data).status_code == 302
    response = client.post("/zayavka/", lead_data, HTTP_ACCEPT="application/json")
    assert response.status_code == 429
    assert Lead.objects.count() == 2


def test_first_touch_utm_attached_to_lead(client, lead_data):
    client.get("/?utm_source=yandex&utm_medium=cpc&utm_campaign=lifts")
    client.get("/?utm_source=google")  # a later touch doesn't overwrite
    client.post("/zayavka/", lead_data)

    lead = Lead.objects.get()
    assert (lead.utm_source, lead.utm_medium, lead.utm_campaign) == ("yandex", "cpc", "lifts")
    assert lead.landing_page == "/?utm_source=yandex&utm_medium=cpc&utm_campaign=lifts"


def test_external_referrer_captured(client, lead_data):
    client.get("/", HTTP_REFERER="https://yandex.ru/search/?text=podemnik")
    client.post("/zayavka/", lead_data)
    assert Lead.objects.get().referrer == "https://yandex.ru/search/?text=podemnik"


def test_page_field_rejects_foreign_urls(client, lead_data):
    lead_data["page"] = "//evil.example/"
    client.post("/zayavka/", lead_data)
    assert Lead.objects.get().source_page == ""


@pytest.fixture
def staff_client(client):
    user = get_user_model().objects.create_superuser("admin", "a@example.com", "pass")
    client.force_login(user)
    return client


def test_admin_list_hides_spam_by_default(staff_client):
    Lead.objects.create(name="Real person", phone="+77001234567")
    Lead.objects.create(name="Spam bot", phone="+77001234567", status=Lead.Status.SPAM)

    html = staff_client.get("/admin/leads/lead/").content.decode()
    assert "Real person" in html and "Spam bot" not in html
    assert "Spam bot" in staff_client.get("/admin/leads/lead/?status__exact=spam").content.decode()


def test_admin_csv_export_neutralises_formulas(staff_client):
    lead = Lead.objects.create(name='=HYPERLINK("http://x")', phone="+77001234567")
    response = staff_client.post("/admin/leads/lead/", {"action": "export_csv", "_selected_action": [lead.pk]})
    body = response.content.decode("utf-8-sig")
    assert response["Content-Type"].startswith("text/csv")
    assert "'=HYPERLINK" in body
    assert "+77001234567" in body


def test_replayed_token_is_spam_but_one_link_is_fine(client, lead_data):
    lead_data["message"] = "Чертёж: https://disk.yandex.ru/d/abc"
    client.post("/zayavka/", lead_data)
    client.post("/zayavka/", lead_data)  # the same page token again: a bot replaying one form
    first, second = Lead.objects.order_by("pk")
    assert first.status == Lead.Status.NEW and first.spam_reason == ""
    assert (second.status, second.spam_reason) == (Lead.Status.SPAM, "token_reused")
