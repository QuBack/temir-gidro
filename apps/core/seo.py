"""Helpers that build absolute URLs and schema.org (JSON-LD) structures."""

from django.conf import settings
from django.templatetags.static import static

from .company import COMPANY


def absolute_url(path: str) -> str:
    """Absolute URL on the canonical origin (never taken from the Host header)."""
    if path.startswith(("http://", "https://")):
        return path
    return f"{settings.SITE_URL}{path}"


def organization_schema() -> dict:
    address = COMPANY["address"]
    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": absolute_url("/#organization"),
        "name": COMPANY["name"],
        "description": str(COMPANY["description"]),
        "url": absolute_url("/"),
        "logo": absolute_url(static("img/logo.svg")),
        "telephone": COMPANY["phone_href"],
        "email": COMPANY["email"],
        "openingHours": COMPANY["opening_hours"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address["street"],
            "addressLocality": address["city"],
            "addressRegion": address["region"],
            "postalCode": address["postal_code"],
            "addressCountry": address["country"],
        },
    }
    if COMPANY["legal_name"]:
        data["legalName"] = COMPANY["legal_name"]
    if COMPANY["social"]:
        data["sameAs"] = COMPANY["social"]
    return data


def breadcrumb_schema(crumbs: list[tuple[str, str]]) -> dict:
    """crumbs: [(title, path), …] from the home page to the current page."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": str(title), "item": absolute_url(path)}
            for i, (title, path) in enumerate(crumbs, start=1)
        ],
    }
