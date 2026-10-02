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
    "phone": "+7 (499) 117-01-31",
    "phone_href": "+74991170131",
    "phone_extra": "+7 (930) 012-95-92",
    "phone_extra_href": "+79300129592",
    "email": "gidro@temir.ru",
    "address": {
        "street": "Чечёрский проезд, д. 24, пом. 1/1",
        "city": "Москва",
        "region": "Москва",
        "postal_code": "",  # TODO
        "country": "RU",
        # Map search query: without the premises number, which Yandex's geocoder
        # misreads as "entrance 1, floor 1, flat 1".
        "map_query": "Москва, Чечёрский проезд, 24",
    },
    # schema.org openingHours format
    "opening_hours": ["Mo-Fr 08:30-17:30"],
    "opening_hours_display": _("Пн–Пт 08:30–17:30"),
    # Profiles: links in the footer and on the contacts page, sameAs in schema.org.
    # icon is a symbol in static/img/icons.svg.
    "social": [
        {"name": "ВКонтакте", "url": "https://vk.ru/temir_gidro", "icon": "vk"},
        {"name": "YouTube", "url": "https://www.youtube.com/@temir-gidro", "icon": "youtube"},
        # Meta is banned in Russia: the law requires this note next to the name.
        {
            "name": "Instagram",
            "url": "https://www.instagram.com/temirgidro/",
            "icon": "instagram",
            "note": _("Instagram принадлежит компании Meta, признанной экстремистской и запрещённой в РФ."),
        },
    ],
}
