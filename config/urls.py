from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import sitemaps
from apps.core.views import favicon, indexnow_key, robots_txt

admin.site.site_header = admin.site.site_title = "Temir-Gidro"
admin.site.index_title = "Управление сайтом"

handler404 = "apps.core.views.page_not_found"

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("favicon.ico", favicon),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps, "template_name": "sitemap.xml"},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(settings.ADMIN_URL, admin.site.urls),
]
if settings.INDEXNOW_KEY:
    urlpatterns.append(path(f"{settings.INDEXNOW_KEY}.txt", indexnow_key))

# Russian (default) has no prefix: /…; other languages: /en/…, /kk/…
urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("", include("apps.leads.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
