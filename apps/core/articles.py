"""Articles: /stati/ and /stati/<slug>/.

Static until the blog app exists: the metadata lives here, each body is a template
in templates/articles/<slug>.html. Newest first.
"""

import datetime

from django.utils.translation import gettext_lazy as _

from .catalog import img

ARTICLES = [
    {
        "slug": "nozhnichnyj-podemnik-konstrukciya-i-bezopasnost",
        "category": _("Статьи"),
        "title": _("Ножничный подъёмник: конструкция, безопасность и управление"),
        "seo_title": _("Ножничный подъёмник: конструкция и безопасность | ТЕМИР ГИДРО"),
        "description": _(
            "Как устроен гидравлический ножничный подъёмник: платформа, гидроцилиндры, маслостанция, защита "
            "от перегруза и концевые выключатели, посты управления, тандем до 20 т. Фото с производства."
        ),
        "text": _("Платформа, гидравлика, системы безопасности и управление — с фото с нашего производства."),
        # Moved from the old site (temir-gidro.ru, «Ножничные подъемники»); its pictures were uploaded in July 2026.
        "date": datetime.date(2026, 7, 1),
        # The engineer quoted in the article; also the author in the BlogPosting markup.
        "author": {"name": "Владимир Теплов"},
        "image": img("articles/nozhnichnyj-podemnik-montazh-platformy", (1448, 1086), widths=(600, 1024, 1448)),
        "image_alt": _("Ножничный подъёмник ТЕМИР ГИДРО в цехе: платформа с сигнальной разметкой и ножничный механизм"),
        "related": ("/podemniki/nozhnichnye/", _("Ножничные подъёмники 1X–4X")),
        "images": {
            "montazh": img("articles/nozhnichnyj-podemnik-montazh-platformy", (1448, 1086), widths=(600, 1024, 1448)),
            "ispytanie": img("articles/nozhnichnyj-podemnik-3x-ispytanie", (1086, 1448), widths=(400, 732, 1086)),
            "s_gruzom": img("articles/nozhnichnyj-podemnik-s-gruzom", (1086, 1448), widths=(400, 732, 1086)),
        },
    },
    {
        "slug": "nozhnichnyj-podemnik-dlya-avtoservisa",
        "category": _("Проекты"),
        "title": _("Ножничный подъёмник для автосервиса: снимаем КПП грузовика в смотровой яме"),
        "seo_title": _("Ножничный подъёмник для автосервиса и смотровой ямы | ТЕМИР ГИДРО"),
        "description": _(
            "Как устроен ножничный подъёмник для снятия КПП грузовика в смотровой яме: до 500 кг, "
            "платформа 900 × 550 мм, встроенная гидростанция, микроконтроллерное управление."
        ),
        "text": _("Проект подъёмника до 500 кг для смотровой ямы: габариты, безопасность и управление."),
        # Published on the old site (temir-gidro.ru) on 7 August 2026.
        "date": datetime.date(2026, 8, 7),
        "image": img("articles/nozhnichnyj-podemnik-dlya-avtoservisa", (1280, 943), widths=(400, 800, 1280)),
        "image_alt": _("Ножничный подъёмник для смотровой ямы автосервиса на колёсной базе"),
        "related": ("/podemniki/nozhnichnye/1x/", _("Ножничный подъёмник 1X")),
        # Pictures inside the body template.
        "images": {
            "work": img("articles/podemnik-dlya-avtoservisa-v-rabote", (732, 1024), widths=(400, 732)),
            "pult": img("articles/pult-upravleniya-podemnikom", (1024, 625), widths=(600, 1024)),
        },
    },
    {
        "slug": "kak-vybrat-nozhnichnyj-podemnik",
        "category": _("Статьи"),
        "title": _("Как выбрать ножничный подъёмник: 5 параметров"),
        "seo_title": _("Как выбрать ножничный подъёмник: 5 главных параметров | ТЕМИР ГИДРО"),
        "description": _(
            "Грузоподъёмность, высота подъёма, размер платформы, привод и защита: на что смотреть при "
            "выборе гидравлического ножничного подъёмника и какие данные нужны для расчёта."
        ),
        "text": _("Грузоподъёмность, высота, платформа, привод и безопасность — на что смотреть."),
        "date": datetime.date(2026, 10, 1),
        "image": img("articles/kak-vybrat-nozhnichnyj-podemnik", (800, 533)),
        "image_alt": _("Гидравлический ножничный подъёмник в цехе"),
        "related": ("/podemniki/nozhnichnye/", _("Ножничные подъёмники 1X–4X")),
    },
    {
        "slug": "podzemnye-kontejnernye-ploshchadki",
        "category": _("Статьи"),
        "title": _("Подземные контейнерные площадки: как они устроены"),
        "seo_title": _("Подземная контейнерная площадка: устройство и подъёмник | ТЕМИР ГИДРО"),
        "description": _(
            "Как работает подземная контейнерная площадка: шахта, гидравлический подъёмник, мусороприёмники "
            "и обслуживание. Что нужно для проекта и чем она лучше обычной площадки во дворе."
        ),
        "text": _("Шахта, гидравлика, мусороприёмники и обслуживание — разбираем по узлам."),
        "date": datetime.date(2026, 10, 1),
        "image": img("articles/podzemnye-kontejnernye-ploshchadki", (800, 533)),
        "image_alt": _("Подземная контейнерная площадка во дворе жилого дома"),
        "related": ("/podemniki/dlya-musornyh-kontejnerov/", _("Подъёмники для мусорных контейнеров")),
    },
    {
        "slug": "svarnoj-ili-razbornyj-gidrocilindr",
        "category": _("Статьи"),
        "title": _("Сварной или разборный гидроцилиндр: что выбрать"),
        "seo_title": _("Сварной или разборный гидроцилиндр: отличия и выбор | ТЕМИР ГИДРО"),
        "description": _(
            "Чем отличаются сварные, разборные и телескопические гидроцилиндры, где какой применять "
            "и какие данные нужны, чтобы заказать гидроцилиндр по чертежу или образцу."
        ),
        "text": _("Чем отличаются конструкции и какую выбрать под вашу технику."),
        "date": datetime.date(2026, 10, 1),
        "image": img("articles/svarnoj-ili-razbornyj-gidrocilindr", (800, 533)),
        "image_alt": _("Гидроцилиндры на производстве"),
        "related": ("/gidrocilindry/", _("Гидроцилиндры на заказ")),
    },
]

for _a in ARTICLES:
    _a["url"] = f"/stati/{_a['slug']}/"
    _a["template"] = f"articles/{_a['slug']}.html"
del _a

BY_SLUG = {a["slug"]: a for a in ARTICLES}


def latest(count=3):
    return sorted(ARTICLES, key=lambda a: a["date"], reverse=True)[:count]
