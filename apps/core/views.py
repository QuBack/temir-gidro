from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from apps.leads.forms import LeadForm

from . import catalog
from .mixins import BreadcrumbsMixin, SeoMixin
from .seo import faq_schema, organization_schema


class HomeView(SeoMixin, TemplateView):
    template_name = "core/home.html"
    # TODO: final wording after the keyword research.
    seo_title = _("Гидравлические подъёмники от производителя — ТЕМИР ГИДРО")
    seo_description = _(
        "Производим ножничные, четырёхстоечные и специальные гидравлические подъёмники и гидроцилиндры "
        "под задачу. Монтаж, гарантия, доставка по России."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lead_form"] = LeadForm.for_request(self.request)
        context["jsonld"] = [organization_schema(), faq_schema(catalog.FAQ)]
        context.update(
            hero_image=catalog.HERO_IMAGE,
            hero_video=catalog.HERO_VIDEO,
            categories=catalog.CATEGORIES,
            cylinders=catalog.CYLINDERS,
            stats=catalog.STATS,
            advantages=catalog.ADVANTAGES,
            steps=catalog.STEPS,
            industries=catalog.INDUSTRIES,
            projects=catalog.PROJECTS,
            faq=catalog.FAQ,
            articles=catalog.ARTICLES,
        )
        return context


class PrivacyView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/privacy.html"
    seo_title = _("Политика конфиденциальности | ТЕМИР ГИДРО")
    seo_description = _("Как ТЕМИР ГИДРО обрабатывает и защищает персональные данные, отправленные через сайт.")

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
