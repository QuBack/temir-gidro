"""Company NAP data (name, address, phone) — the single source for the header,
footer, contacts and schema.org markup. Must match Yandex.Business, Google
Business Profile and 2GIS exactly.

ТЕМИР ГИДРО is the trademark; the legal entity is ООО «ПРОМСПЕЦМЕТ».
"""

from django.utils.translation import gettext_lazy as _

COMPANY = {
    "name": "ТЕМИР ГИДРО",
    "legal_name": "ООО «ПРОМСПЕЦМЕТ»",
    "description": _(
        "Производство гидравлических подъёмников и гидроцилиндров. Проект под задачу, поставка и монтаж по России."
    ),
    "phone": "8 (800) 333-75-80",
    "phone_href": "+78003337580",
    "phone_extra": "+7 (499) 117-01-31",
    "phone_extra_href": "+74991170131",
    "email": "gidro@temir.ru",  # TODO: confirm — the new domain is temir-gidro.com
    "address": {
        "street": "Чечёрский проезд, д. 24, пом. 1/1",
        "city": "Москва",
        "region": "Москва",
        "postal_code": "",  # TODO
        "country": "RU",
    },
    # schema.org openingHours format
    "opening_hours": ["Mo-Fr 08:30-17:30"],
    "opening_hours_display": _("Пн–Пт 08:30–17:30"),
    "social": [],  # full profile URLs (VK, Telegram channel, RUTUBE …)
}
