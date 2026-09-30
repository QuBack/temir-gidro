from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "core"

# URL slugs are Russian transliteration on purpose: Yandex matches and highlights
# query words in them. They are translatable: msgid is the Russian slug, other
# languages translate it in locale/<lang>/LC_MESSAGES/django.po.
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(_("politika-konfidencialnosti/"), views.PrivacyView.as_view(), name="privacy"),
    path(_("podemniki/"), views.CatalogView.as_view(), name="catalog"),
    path(_("podemniki/<slug:slug>/"), views.EquipmentView.as_view(), name="equipment"),
    path(_("kontakty/"), views.ContactsView.as_view(), name="contacts"),
    path(_("o-kompanii/"), views.AboutView.as_view(), name="about"),
]
