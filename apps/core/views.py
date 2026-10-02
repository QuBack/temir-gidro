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

from . import articles, catalog, cylinders, lift_models
from .company import COMPANY
from .mixins import BreadcrumbsMixin, SeoMixin
from .seo import (
    about_page_schema,
    article_schema,
    collection_schema,
    faq_schema,
    organization_schema,
    product_schema,
)


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
            equipment_tiles=catalog.EQUIPMENT_TILES,
            cylinders=catalog.CYLINDERS,
            stats=catalog.STATS,
            advantages=catalog.ADVANTAGES,
            steps=catalog.STEPS_TIMELINE,
            industries=catalog.INDUSTRIES,
            projects=catalog.PROJECTS,
            faq=catalog.FAQ,
            articles=articles.latest(3),
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
            scissor_series=catalog.SCISSOR_SERIES,
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


class ModelView(SeoMixin, BreadcrumbsMixin, TemplateView):
    """Serial model page (scissor lift 1X, …) from lift_models.MODELS."""

    template_name = "core/model.html"

    def dispatch(self, request, *args, **kwargs):
        self.model = lift_models.MODELS.get((kwargs["slug"], kwargs["model"]))
        if self.model is None:
            raise Http404
        self.line = catalog.EQUIPMENT[kwargs["slug"]]
        return super().dispatch(request, *args, **kwargs)

    def get_seo(self):
        model = self.model
        return {"seo_title": model["seo_title"], "seo_description": model["seo_description"], "noindex": False}

    def get_breadcrumbs(self):
        line_url = reverse("core:equipment", args=[self.model["line"]])
        return [
            (_("Подъёмники"), reverse("core:catalog")),
            (self.line["title"], line_url),
            (self.model["name"], self.request.path),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model
        image = model["images"][0]["image"] if model["images"] else self.line["image"]
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            product_schema(
                model["title"],
                model["seo_description"],
                static(f"img/{image['src']}-{image['widths'][-1]}.webp"),
                self.request.path,
                properties=model["specs"],
                model=model["name"],
            ),
            faq_schema(model["faq"]),
        ]
        context.update(
            model=model,
            line=self.line,
            short_specs=lift_models.short_specs(model),
            kit_points=lift_models.kit_points(model),
            kit_overlay=lift_models.kit_overlay(model),
            delivery=lift_models.DELIVERY,
            documents=lift_models.DOCUMENTS,
            advantages=catalog.ADVANTAGES,
            siblings=[m for m in lift_models.MODELS.values() if m["line"] == model["line"]],
            lead_form=LeadForm.for_request(self.request),
        )
        return context


def _image_url(image):
    return static(f"img/{image['src']}-{image['widths'][-1]}.webp")


class CylindersView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/cylinders.html"
    seo_title = cylinders.PAGE["seo_title"]
    seo_description = cylinders.PAGE["seo_description"]

    def get_breadcrumbs(self):
        return [(_("Гидроцилиндры"), reverse("core:cylinders"))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = cylinders.PAGE
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            product_schema(
                page["title"], page["seo_description"], _image_url(page["image"]), self.request.path,
                properties=page["specs"],
            ),
            faq_schema(page["faq"]),
        ]
        context.update(page=page, lead_form=LeadForm.for_request(self.request))
        return context


class ArticleListView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/article_list.html"
    seo_title = _("Статьи о подъёмниках и гидравлике — ТЕМИР ГИДРО")
    seo_description = _(
        "Как выбрать ножничный подъёмник, как устроены подземные контейнерные площадки, какой гидроцилиндр "
        "выбрать, и наши проекты — статьи инженеров ТЕМИР ГИДРО."
    )

    def get_breadcrumbs(self):
        return [(_("Статьи"), reverse("core:articles"))]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = articles.latest(len(articles.ARTICLES))
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            collection_schema(self.seo_title, reverse("core:articles"), [(a["title"], a["url"]) for a in items]),
        ]
        context["articles"] = items
        return context


class ArticleView(SeoMixin, BreadcrumbsMixin, TemplateView):
    template_name = "core/article.html"

    def dispatch(self, request, *args, **kwargs):
        self.article = articles.BY_SLUG.get(kwargs["slug"])
        if self.article is None:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_seo(self):
        a = self.article
        return {"seo_title": a["seo_title"], "seo_description": a["description"], "noindex": False}

    def get_breadcrumbs(self):
        return [(_("Статьи"), reverse("core:articles")), (self.article["title"], self.request.path)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        a = self.article
        context["jsonld"] = [
            organization_schema(),
            *context.get("jsonld", []),
            article_schema(a, _image_url(a["image"]), self.request.path),
        ]
        context.update(
            article=a,
            og_type="article",
            og_image=f"{settings.SITE_URL}{_image_url(a['image'])}",
            more=[x for x in articles.latest(4) if x["slug"] != a["slug"]][:3],
            lead_form=LeadForm.for_request(self.request),
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
        "Телефон +7 (499) 117-01-31, почта и адрес ТЕМИР ГИДРО в Москве. Оставьте заявку — перезвоним в рабочее время."
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
