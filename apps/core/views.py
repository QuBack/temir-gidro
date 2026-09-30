from urllib.parse import quote

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from apps.leads.forms import LeadForm

from . import catalog
from .company import COMPANY
from .mixins import BreadcrumbsMixin, SeoMixin
from .seo import about_page_schema, collection_schema, faq_schema, organization_schema, product_schema


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
            hero_lift=catalog.HERO_LIFT,
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


class CatalogView(SeoMixin, BreadcrumbsMixin, TemplateView):
    """Section page: all lift lines."""

    template_name = "core/catalog.html"
    seo_title = _("Каталог гидравлических подъёмников — ТЕМИР ГИДРО")
    seo_description = _(
        "Ножничные, четырёхстоечные, автомобильные, консольные подъёмники, подъёмники для контейнеров "
        "и окрасочных камер. Серийные модели и оборудование по ТЗ от производителя."
    )

    def get_breadcrumbs(self):
        return [(_("Подъёмники"), reverse("core:catalog"))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            collection_schema(
                self.seo_title, reverse("core:catalog"), [(c["title"], c["url"]) for c in catalog.CATEGORIES]
            ),
        ]
        context.update(
            lead_form=LeadForm.for_request(self.request),
            categories=catalog.CATEGORIES,
            industries=catalog.INDUSTRIES,
        )
        return context


class EquipmentView(SeoMixin, BreadcrumbsMixin, TemplateView):
    """Equipment line page (scissor lifts, four-post lifts, …) from catalog.EQUIPMENT."""

    template_name = "core/equipment.html"

    def dispatch(self, request, *args, **kwargs):
        self.item = catalog.EQUIPMENT.get(kwargs["slug"])
        if self.item is None:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_seo(self):
        return {"seo_title": self.item["seo_title"], "seo_description": self.item["seo_description"], "noindex": False}

    def get_breadcrumbs(self):
        return [(_("Подъёмники"), reverse("core:catalog")), (self.item["title"], self.request.path)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.item
        image = item["image"]
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            product_schema(
                item["title"],
                item["seo_description"],
                static(f"img/{image['src']}-{image['widths'][-1]}.webp"),
                self.request.path,
            ),
            faq_schema(item["faq"]),
        ]
        context.update(
            item=item,
            lead_form=LeadForm.for_request(self.request),
            hero_lift=catalog.HERO_LIFT,
            related=[c for c in catalog.CATEGORIES if c["url"] != self.request.path],
        )
        return context


class AboutView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/about.html"
    seo_title = _("О компании ТЕМИР ГИДРО — производитель подъёмников")
    seo_description = _(
        "ТЕМИР ГИДРО проектирует и производит гидравлические подъёмники и гидроцилиндры: "
        "10+ лет производства, 3000+ проектов. Испытания, монтаж и гарантия."
    )

    def get_breadcrumbs(self):
        return [(_("О компании"), reverse("core:about"))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            about_page_schema(self.seo_title, reverse("core:about")),
        ]
        context.update(
            lead_form=LeadForm.for_request(self.request),
            hero_image=catalog.HERO_IMAGE,
            about_bg=catalog.ABOUT_BG,
            stats=catalog.STATS,
            advantages=catalog.ADVANTAGES,
            steps=catalog.STEPS,
            categories=catalog.CATEGORIES,
            cylinders=catalog.CYLINDERS,
        )
        return context


class ContactsView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/contacts.html"
    seo_title = _("Контакты — ТЕМИР ГИДРО, гидравлические подъёмники в Москве")
    seo_description = _(
        "Телефон 8 (800) 333-75-80, почта и адрес ТЕМИР ГИДРО в Москве. Оставьте заявку — перезвоним в рабочее время."
    )

    def get_breadcrumbs(self):
        return [(_("Контакты"), reverse("core:contacts"))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = f"{COMPANY['address']['city']}, {COMPANY['address']['street']}"
        query = quote(COMPANY["address"]["map_query"], safe="")
        context["jsonld"] = [organization_schema(), *context.get("jsonld", [])]
        context.update(
            lead_form=LeadForm.for_request(self.request),
            contacts_bg=catalog.CONTACTS_BG,
            address=address,
            map_links={
                "yandex": f"https://yandex.ru/maps/?text={query}",
                "gis": f"https://2gis.ru/moscow/search/{query}",
            },
            map_embed=f"https://yandex.ru/map-widget/v1/?text={query}&z=16",
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
