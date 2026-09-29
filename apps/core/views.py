from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from apps.leads.forms import LeadForm

from .mixins import BreadcrumbsMixin, SeoMixin
from .seo import organization_schema


class HomeView(SeoMixin, TemplateView):
    template_name = "core/home.html"
    # TODO: final wording after the keyword research.
    seo_title = _("Подъёмники — продажа, монтаж и обслуживание | Temir-Gidro")
    seo_description = _(
        "Temir-Gidro: подъёмники с доставкой, монтажом и сервисным обслуживанием. "
        "Оставьте заявку — перезвоним и подберём оборудование."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lead_form"] = LeadForm.for_request(self.request)
        context["jsonld"] = [organization_schema()]
        return context


class PrivacyView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/privacy.html"
    seo_title = _("Политика конфиденциальности | Temir-Gidro")
    seo_description = _("Как Temir-Gidro обрабатывает и защищает персональные данные, отправленные через сайт.")

    def get_breadcrumbs(self):
        return [(_("Политика конфиденциальности"), reverse("core:privacy"))]


@require_GET
def robots_txt(request):
    return render(
        request,
        "robots.txt",
        {"sitemap_url": f"{settings.SITE_URL}/sitemap.xml", "seo_indexing": settings.SEO_INDEXING},
        content_type="text/plain; charset=utf-8",
    )


def page_not_found(request, exception):
    return render(request, "404.html", {"noindex": True, "seo_title": _("Страница не найдена")}, status=404)
