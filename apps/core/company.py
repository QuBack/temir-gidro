"""Company NAP data (name, address, phone) — the single source for the header,
footer, contacts and schema.org markup. Must match Yandex.Business, Google
Business Profile and 2GIS exactly.

TODO: fill in real data.
"""

from django.utils.translation import gettext_lazy as _

COMPANY = {
    "name": "Temir-Gidro",
    "legal_name": "",
    "description": _("Продажа, монтаж и обслуживание подъёмников."),
    "phone": "+7 (000) 000-00-00",
    "phone_href": "+70000000000",
    "email": "info@example.com",
    "address": {
        "street": "",
        "city": "",
        "region": "",
        "postal_code": "",
        "country": "KZ",
    },
    # schema.org openingHours format
    "opening_hours": ["Mo-Fr 09:00-18:00"],
    "social": [],  # full profile URLs (Instagram, VK, Telegram channel …)
}
