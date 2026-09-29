import time

import pytest
from django.core import signing

from apps.leads.forms import _TOKEN_SALT

SITE = "https://temir-gidro.example"


@pytest.fixture(autouse=True)
def _site_settings(settings):
    settings.SITE_URL = SITE
    settings.SEO_INDEXING = True
    settings.LANGUAGES = [("ru", "Русский")]
    settings.ADMIN_URL = "admin/"
    settings.TELEGRAM_BOT_TOKEN = ""
    settings.YANDEX_METRIKA_ID = ""
    # Hashed-manifest storage needs collectstatic; tests don't run it.
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


@pytest.fixture
def multilingual(settings):
    settings.LANGUAGES = [("ru", "Русский"), ("en", "English")]


@pytest.fixture
def lead_data():
    """A valid human submission: the form was rendered 10 seconds ago."""
    return {
        "name": "Иван",
        "phone": "+7 (700) 123-45-67",
        "email": "",
        "message": "Нужен подъёмник",
        "consent": "on",
        "website": "",
        "token": signing.dumps(int(time.time()) - 10, salt=_TOKEN_SALT),
        "page": "/",
    }
