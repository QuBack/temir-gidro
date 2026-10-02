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
        # Square brand mark (180×180): search engines need a logo of at least 112×112.
        "logo": absolute_url(static("img/apple-touch-icon.png")),
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


def product_schema(name, description, image_path: str, path: str, properties=(), model="") -> dict:
    """A catalog line or model as schema.org Product, made by the organization.
    properties: [(name, value), …] — known specs as PropertyValue."""
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": str(name),
        "description": str(description),
        "image": absolute_url(image_path),
        "url": absolute_url(path),
        "brand": {"@type": "Brand", "name": COMPANY["name"]},
        "manufacturer": {"@id": absolute_url("/#organization")},
    }
    if model:
        data["model"] = str(model)
    if properties:
        data["additionalProperty"] = [
            {"@type": "PropertyValue", "name": str(k), "value": str(v)} for k, v in properties if v is not None
        ]
    return data


def collection_schema(name, path: str, items: list[tuple[str, str]]) -> dict:
    """A section page listing catalog lines: items are [(name, path), …]."""
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": str(name),
        "url": absolute_url(path),
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": str(title), "url": absolute_url(url)}
                for i, (title, url) in enumerate(items, start=1)
            ],
        },
    }


def about_page_schema(name, path: str) -> dict:
    """The "About" page, pointing at the organization described on it."""
    return {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": str(name),
        "url": absolute_url(path),
        "about": {"@id": absolute_url("/#organization")},
    }


def faq_schema(items: list[tuple[str, str]]) -> dict:
    """items: [(question, answer), …] — must match the visible FAQ block."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": str(q), "acceptedAnswer": {"@type": "Answer", "text": str(a)}}
            for q, a in items
        ],
    }


def article_schema(article, image_path: str, path: str) -> dict:
    """An article as schema.org BlogPosting, published by the organization."""
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": str(article["title"]),
        "description": str(article["description"]),
        "image": absolute_url(image_path),
        "url": absolute_url(path),
        "mainEntityOfPage": absolute_url(path),
        "datePublished": article["date"].isoformat(),
        "author": {"@id": absolute_url("/#organization")},
        "publisher": {"@id": absolute_url("/#organization")},
        "inLanguage": "ru",
    }
