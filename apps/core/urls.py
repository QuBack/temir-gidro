from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "core"

# URL slugs are translatable: msgid is the Russian slug, other languages
# translate it in locale/<lang>/LC_MESSAGES/django.po.
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(_("politika-konfidencialnosti/"), views.PrivacyView.as_view(), name="privacy"),
]
