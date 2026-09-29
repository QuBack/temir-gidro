from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .seo import breadcrumb_schema


class SeoMixin:
    """Page-level SEO meta. Values live in the view (and later in the admin),
    not in templates, so they can be edited without touching markup."""

    seo_title = ""
    seo_description = ""
    noindex = False  # service pages: form, thank-you page, etc.

    def get_seo(self) -> dict:
        return {"seo_title": self.seo_title, "seo_description": self.seo_description, "noindex": self.noindex}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_seo())
        return context


class BreadcrumbsMixin:
    """Renders visible breadcrumbs and the matching BreadcrumbList JSON-LD.
    Subclasses return the trail after "Home": [(title, path), …]."""

    def get_breadcrumbs(self) -> list[tuple[str, str]]:
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if crumbs := self.get_breadcrumbs():
            crumbs = [(_("Главная"), reverse("core:home")), *crumbs]
            context["breadcrumbs"] = crumbs
            context.setdefault("jsonld", []).append(breadcrumb_schema(crumbs))
        return context
