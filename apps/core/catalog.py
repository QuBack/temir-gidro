"""Home page content for the prototype.

Static data until the catalog / articles / projects models exist; then these
lists move to the database and the admin. URLs follow the planned structure —
the pages behind them are not built yet.
"""

from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


def img(src, size, widths=(400, 800)):
    return {"src": src, "size": size, "widths": widths}


# Full-width workshop photo in the hero — the LCP image.
HERO_IMAGE = img("hero/gidravlicheskie-podemniki", (1920, 765), widths=(768, 1280, 1920))
# Generated drawing-style backgrounds (illustrations, never passed off as photos).
CONTACTS_BG = img("backgrounds/chertezh-nozhnichnogo-podemnika", (1672, 941), widths=(768, 1280, 1672))
ABOUT_BG = img("backgrounds/chertezh-gidrocilindra", (1672, 941), widths=(768, 1280, 1672))
# Configurator fallback when JS is off (with JS a live SVG scheme replaces it).
HERO_LIFT = img("catalog/nozhnichnyj-podemnik-3x", (800, 1289))
# Drop a muted 6–15 s loop into static/video/ and set the file name here;
# it plays over the hero photo.
HERO_VIDEO = None  # e.g. "video/hero.mp4"

# Renders of the models (transparent background), shared by the catalog, the menu and the tiles.
SCISSOR_1X = img("catalog/nozhnichnyj-podemnik", (800, 486))
SCISSOR_2X = img("catalog/nozhnichnyj-podemnik-2x", (800, 1080))
SCISSOR_3X = img("catalog/nozhnichnyj-podemnik-3x", (800, 1289))
PAINT_1X = img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490))
PAINT_2D = img("catalog/podemnik-dlya-okrasochnoj-kamery-2d", (800, 497))

CATEGORIES = [
    {
        "title": _("Ножничные подъёмники"),
        "url": "/podemniki/nozhnichnye/",
        "text": _("Серия 1X–4X: от одной до четырёх пар ножниц. Грузовые платформы для складов, цехов и погрузки."),
        "facts": [_("до 10 т"), _("до 6 м")],
        # The 3X render is the configurator fallback; the catalog shows the single-pair 1X.
        "image": img("catalog/nozhnichnyj-podemnik", (800, 486)),
        "featured": True,
    },
    {
        "title": _("Четырёхстоечные подъёмники"),
        "url": "/podemniki/chetyrehstoechnye/",
        "text": _("Самонесущая конструкция на сдвоенных цепях для автосервиса и парковки."),
        "image": img("catalog/chetyrehstoechnyj-podemnik", (800, 531)),
    },
    {
        "title": _("Подъёмники для мусорных контейнеров"),
        "url": "/podemniki/dlya-musornyh-kontejnerov/",
        "text": _("Подземные контейнерные площадки: баки скрыты в шахте и поднимаются к вывозу."),
        "facts": [_("до 8 т")],
        "image": img("catalog/podemnik-dlya-musornyh-kontejnerov", (800, 800)),
    },
    {
        "title": _("Подъёмники для окрасочных камер"),
        "url": "/podemniki/dlya-okrasochnyh-kamer/",
        "text": _("Рабочие платформы 1X и 2D для покраски крупногабаритных изделий."),
        "image": img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490)),
    },
    {
        "title": _("Автомобильные подъёмники"),
        "url": "/podemniki/avtomobilnye/",
        "text": _("Подъём автомобилей между уровнями паркинга и в шоурумах."),
        "image": img("catalog/avtomobilnyj-podemnik", (220, 300), widths=(220,)),
    },
    {
        "title": _("Консольные подъёмники"),
        "url": "/podemniki/konsolnye/",
        "text": _("Модель 1L для подъёма грузов между этажами вдоль стены."),
        "image": img("catalog/konsolnyj-podemnik", (124, 293), widths=(124,)),
    },
]

CYLINDERS = {
    "title": _("Гидроцилиндры"),
    "url": "/gidrocilindry/",
    "text": _(
        "Проектируем и изготавливаем гидроцилиндры по чертежу, образцу или техническому заданию: "
        "сварные, разборные и телескопические."
    ),
    "specs": [
        (_("Диаметр поршня"), _("40–250 мм")),
        (_("Ход поршня"), _("50–3000 мм")),
        (_("Рабочее давление"), _("16–32 МПа")),
    ],
    "image": img("catalog/gidrocilindry", (800, 389)),
    "photos": [img(f"photos/proizvodstvo-gidrocilindrov-{i}", (300, 300), widths=(300,)) for i in (1, 2, 3)],
}

STATS = [
    ("10+", _("лет производства")),
    ("3000+", _("реализованных проектов")),
    ("4000+", _("разработанных моделей")),
    ("24 ч", _("на расчёт стоимости")),
]

# (title, text, icon)
ADVANTAGES = [
    (
        _("Собственное производство"),
        _("Проектируем и производим сами — без посредников и перепродажных наценок."),
        "factory",
    ),
    (
        _("Под вашу задачу"),
        _("Размер платформы, высота и грузоподъёмность — под объект, а не из каталога."),
        "ruler-dimension-line",
    ),
    (
        _("Испытания каждого изделия"),
        _("100% контроль: гидравлические испытания на заявленные параметры перед отгрузкой."),
        "gauge",
    ),
    (
        _("Монтаж и сервис"),
        _("Устанавливаем и настраиваем оборудование на объекте, обслуживаем после запуска."),
        "wrench",
    ),
    (
        _("Гарантия и документация"),
        _("Заводская гарантия, паспорт и полный комплект технической документации."),
        "shield-check",
    ),
    (_("Доставка по России"), _("Отгружаем оборудование в любой регион."), "truck"),
]

# (title, text, icon) — icons are symbols in static/img/icons.svg.
STEPS = [
    (
        _("Заявка"),
        _("Габариты платформы, высота подъёма и грузоподъёмность — этого достаточно для старта."),
        "clipboard-pen",
    ),
    (_("Расчёт"), _("Инженерный расчёт нагрузок, смета и сроки — в течение суток."), "calculator"),
    (_("Проект"), _("Разрабатываем и согласуем с вами конструкторскую документацию."), "drafting-compass"),
    (_("Производство"), _("Изготовление, окраска и испытания на соответствие параметрам."), "cog"),
    (_("Монтаж"), _("Поставка, монтаж и пусконаладка на объекте заказчика."), "hard-hat"),
]

# (title, text, url, icon)
INDUSTRIES = [
    (
        _("Склады и логистика"),
        _("Погрузка, перегрузочные площадки, подъём между уровнями."),
        "/podemniki/nozhnichnye/",
        "forklift",
    ),
    (
        _("Промышленность"),
        _("Рабочие платформы и подъём тяжёлых узлов в цехах."),
        "/podemniki/nozhnichnye/",
        "factory",
    ),
    (
        _("Автосервис и паркинг"),
        _("Четырёхстоечные и автомобильные подъёмники."),
        "/podemniki/chetyrehstoechnye/",
        "car",
    ),
    (
        _("ЖКХ и благоустройство"),
        _("Подземные контейнерные площадки для дворов."),
        "/podemniki/dlya-musornyh-kontejnerov/",
        "trash-2",
    ),
    (
        _("Покрасочные производства"),
        _("Платформы для окрасочных камер."),
        "/podemniki/dlya-okrasochnyh-kamer/",
        "spray-can",
    ),
    (
        _("Спецтехника"),
        _("Гидроцилиндры для строительной и коммунальной техники."),
        "/gidrocilindry/",
        "tractor",
    ),
]

# TODO: replace with real objects (photo, city, task, result) once available.
PROJECTS = [
    {
        "title": _("Подземная контейнерная площадка"),
        "text": _("Жилой квартал: баки скрыты под землёй, двор свободен."),
        "image": img("photos/podzemnaya-kontejnernaya-ploshchadka", (1024, 534), widths=(600, 1024)),
        "url": "/podemniki/dlya-musornyh-kontejnerov/",
    },
    {
        "title": _("Четырёхстоечный подъёмник для паркинга"),
        "text": _("Два машино-места на одной площади."),
        "image": img("photos/chetyrehstoechnyj-podemnik-avtomobil", (1024, 683), widths=(600, 1024)),
        "url": "/podemniki/chetyrehstoechnye/",
    },
    {
        "title": _("Проект подъёмника под объект"),
        "text": _("Схема элементов и узлов — согласуем до начала производства."),
        "image": img("photos/shema-podemnika-dlya-kontejnerov", (1200, 848), widths=(600, 1200)),
        "url": "/podemniki/dlya-musornyh-kontejnerov/",
    },
]

FAQ = [
    (
        _("Сколько стоит подъёмник?"),
        _(
            "Цена зависит от конструкции, поэтому мы считаем её под задачу. Укажите габариты платформы "
            "(длина и ширина), высоту подъёма и грузоподъёмность — пришлём расчёт в течение суток."
        ),
    ),
    (
        _("Можно ли изготовить подъёмник нестандартного размера?"),
        _("Да. Мы проектируем оборудование по техническому заданию, чертежу или образцу заказчика."),
    ),
    (
        _("Вы доставляете оборудование в регионы?"),
        _("Да, отгружаем в любой регион России. Стоимость доставки включаем в коммерческое предложение."),
    ),
    (
        _("Кто выполняет монтаж?"),
        _("Наши специалисты: поставка, монтаж и пусконаладка на объекте, затем сервисное обслуживание."),
    ),
    (
        _("Какая гарантия?"),
        _("Заводская гарантия производителя, паспорт изделия и полный комплект технической документации."),
    ),
]

# TODO: real articles come from the blog app. Covers are AI-generated placeholders (Codex).
ARTICLES = [
    {
        "title": _("Как выбрать ножничный подъёмник: 5 параметров"),
        "text": _("Грузоподъёмность, высота, платформа, привод и безопасность — на что смотреть."),
        "url": "/stati/kak-vybrat-nozhnichnyj-podemnik/",
        "image": img("articles/kak-vybrat-nozhnichnyj-podemnik", (800, 533)),
    },
    {
        "title": _("Подземные контейнерные площадки: как они устроены"),
        "text": _("Шахта, гидравлика, крышка и обслуживание — разбираем по узлам."),
        "url": "/stati/podzemnye-kontejnernye-ploshchadki/",
        "image": img("articles/podzemnye-kontejnernye-ploshchadki", (800, 533)),
    },
    {
        "title": _("Сварной или разборный гидроцилиндр"),
        "text": _("Чем отличаются конструкции и какую выбрать под вашу технику."),
        "url": "/stati/svarnoj-ili-razbornyj-gidrocilindr/",
        "image": img("articles/svarnoj-ili-razbornyj-gidrocilindr", (800, 533)),
    },
]


def scissor_icon(pairs, pair_height=26, width=64):
    """Side-view pictogram of a scissor lift: platform, `pairs` crossed arm
    pairs, base frame. Taller series get taller icons."""
    top, frame = 8, 6
    bottom = top + pairs * pair_height
    lines = []
    for k in range(pairs):
        y1, y2 = top + k * pair_height, top + (k + 1) * pair_height
        lines += [(8, y1, width - 8, y2), (width - 8, y1, 8, y2)]
    return {
        "width": width,
        "height": bottom + frame,
        "top": top - frame,
        "bottom": bottom,
        "frame": frame,
        "lines": lines,
    }


# Equipment line pages: /podemniki/<slug>/. Static until the catalog models exist.
# TODO: series specs (height, load, platform) come from the client — see todo.md.
EQUIPMENT = {
    "nozhnichnye": {
        "title": _("Ножничные подъёмники"),
        "seo_title": _("Ножничные подъёмники от производителя — ТЕМИР ГИДРО"),
        "seo_description": _(
            "Гидравлические ножничные подъёмники серий 1X–4X: грузоподъёмность до 10 т, высота подъёма до 6 м. "
            "Размер платформы под задачу, монтаж и гарантия."
        ),
        "lead": _(
            "Грузовые платформы для складов, цехов и погрузки. Размер платформы, высоту подъёма "
            "и грузоподъёмность подбираем под объект."
        ),
        "image": img("catalog/nozhnichnyj-podemnik", (800, 486)),
        # Set in ГОСТ lettering, where "т" reads like "m": kg and mm, as on drawings.
        "facts": [
            (_("до 10 000 кг"), _("Грузоподъёмность")),
            (_("до 6000 мм"), _("Высота подъёма")),
            ("1–4", _("Пар ножниц")),
            (_("по ТЗ"), _("Платформа")),
        ],
        "models_title": _("Серии 1X–4X"),
        "models_lead": _("Серия — это число пар ножниц: чем их больше, тем выше подъём при той же длине платформы."),
        # Each model shows an `image` or, until photos arrive, an `icon` pictogram.
        "models": [
            {"name": _("Серия 1X"), "slug": "1x", "label": _("Одна пара ножниц"), "image": SCISSOR_1X, "specs": []},
            {"name": _("Серия 2X"), "slug": "2x", "label": _("Две пары ножниц"), "image": SCISSOR_2X, "specs": []},
            {"name": _("Серия 3X"), "slug": "3x", "label": _("Три пары ножниц"), "image": SCISSOR_3X, "specs": []},
            {
                "name": _("Серия 4X"),
                "slug": "4x",
                "label": _("Четыре пары ножниц"),
                "icon": scissor_icon(4),
                "specs": [],
            },
        ],
        "applications": [
            (_("Склады и логистика"), _("Погрузка, перегрузочные площадки, подъём между уровнями."), None),
            (_("Промышленность"), _("Рабочие платформы и подъём тяжёлых узлов в цехах."), None),
            (
                _("Покрасочные производства"),
                _("Рабочие платформы для окрасочных камер."),
                "/podemniki/dlya-okrasochnyh-kamer/",
            ),
        ],
        "gallery": [
            {
                "image": img("hero/gidravlicheskie-podemniki", (1920, 765), widths=(768, 1280, 1920)),
                "alt": _("Ножничные подъёмники ТЕМИР ГИДРО в цехе"),
                "photo": True,
            },
            {"image": img("catalog/nozhnichnyj-podemnik-3x", (800, 1289)), "alt": _("Ножничный подъёмник серии 3X")},
            {
                "image": img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490)),
                "alt": _("Ножничная рабочая платформа для окрасочной камеры"),
            },
        ],
        "faq": [FAQ[0], FAQ[1], FAQ[3], FAQ[4]],
        "configurator": True,
    },
    "dlya-okrasochnyh-kamer": {
        "title": _("Подъёмники для окрасочных камер"),
        "seo_title": _("Подъёмники для окрасочных камер — ТЕМИР ГИДРО"),
        "seo_description": _(
            "Гидравлические рабочие платформы 1X и 2D для окрасочных камер и покраски крупногабаритных изделий. "
            "Размер платформы под камеру, монтаж и гарантия."
        ),
        "lead": _(
            "Рабочие платформы для покраски крупногабаритных изделий. Размер платформы и высоту подъёма "
            "подбираем под вашу камеру."
        ),
        "image": img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490)),
        "facts": [
            ("1X, 2D", _("Модели")),
            (_("по ТЗ"), _("Платформа")),
            (_("по ТЗ"), _("Высота подъёма")),
            (_("24 ч"), _("Расчёт стоимости")),
        ],
        "models_title": _("Модели"),
        "models_lead": _(
            "Две модели рабочих платформ. Какая подойдёт — зависит от изделий и размеров камеры: подскажем при расчёте."
        ),
        # TODO: both models' descriptions come with the old site's media (todo.md).
        "models": [
            {
                "name": "1X",
                "slug": "1x",
                "label": _("Рабочая платформа"),
                "image": img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490)),
                "specs": [],
            },
            {
                "name": "2D",
                "slug": "2d",
                "label": _("Рабочая платформа"),
                "image": PAINT_2D,
                "specs": [],
            },
        ],
        "applications": [
            (_("Покрасочные производства"), _("Рабочие платформы для окрасочных камер."), None),
            (_("Промышленность"), _("Рабочие платформы и подъём тяжёлых узлов в цехах."), None),
        ],
        "gallery": [
            {
                "image": img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490)),
                "alt": _("Рабочая платформа для окрасочной камеры"),
            },
        ],
        "faq": [FAQ[0], FAQ[1], FAQ[3], FAQ[4]],
        "configurator": True,
    },
}


def _model(name, label, url, image=None, icon=None, placeholder=False):
    return {"name": name, "label": label, "url": url, "image": image, "icon": icon, "placeholder": placeholder}


def _placeholders(cat, count=3):
    """Stub cards until the old site's media and model list arrive (see todo.md)."""
    return [
        _model(
            format_lazy("{} {}", _("Модель"), n),
            _("Скоро в каталоге"),
            cat["url"],
            image=cat["image"],
            placeholder=True,
        )
        for n in range(1, count + 1)
    ]


# Models shown in the header mega-menu, keyed by category URL.
_SCISSORS = "/podemniki/nozhnichnye/"
_MODELS = {
    _SCISSORS: [
        _model(
            _("Серия 1X"),
            _("Одна пара ножниц"),
            _SCISSORS + "#seriya-1x",
            image=SCISSOR_1X,
        ),
        _model(_("Серия 2X"), _("Две пары ножниц"), _SCISSORS + "#seriya-2x", image=SCISSOR_2X),
        _model(_("Серия 3X"), _("Три пары ножниц"), _SCISSORS + "#seriya-3x", image=SCISSOR_3X),
        _model(_("Серия 4X"), _("Четыре пары ножниц"), _SCISSORS + "#seriya-4x", icon=scissor_icon(4)),
    ],
    "/podemniki/dlya-okrasochnyh-kamer/": [
        _model(
            "1X",
            _("Рабочая платформа"),
            "/podemniki/dlya-okrasochnyh-kamer/#seriya-1x",
            image=img("catalog/podemnik-dlya-okrasochnoj-kamery", (800, 490)),
        ),
        _model(
            "2D",
            _("Рабочая платформа"),
            "/podemniki/dlya-okrasochnyh-kamer/#seriya-2d",
            image=PAINT_2D,
        ),
    ],
    "/podemniki/konsolnye/": [
        _model(
            "1L",
            _("Подъём грузов между этажами"),
            "/podemniki/konsolnye/",
            image=img("catalog/konsolnyj-podemnik", (124, 293), widths=(124,)),
        ),
    ],
}
for _cat in CATEGORIES:
    _cat["models"] = _MODELS.get(_cat["url"]) or _placeholders(_cat)
del _cat

# Photo tiles on the catalog page: the 1X–4X series.
SCISSOR_SERIES = {"title": _("Ножничные подъёмники"), "url": _SCISSORS, "models": _MODELS[_SCISSORS]}

# Home page tiles: every model, each with its render. Scissor series first (a row of four).
_PAINT = "/podemniki/dlya-okrasochnyh-kamer/"
EQUIPMENT_TILES = [
    {"title": _("Ножничный подъёмник 1X"), "label": _("Одна пара ножниц"), "url": _SCISSORS + "#seriya-1x",
     "image": SCISSOR_1X},
    {"title": _("Ножничный подъёмник 2X"), "label": _("Две пары ножниц"), "url": _SCISSORS + "#seriya-2x",
     "image": SCISSOR_2X},
    {"title": _("Ножничный подъёмник 3X"), "label": _("Три пары ножниц"), "url": _SCISSORS + "#seriya-3x",
     "image": SCISSOR_3X},
    # TODO: 4X has no render yet — it shows the pictogram until one arrives.
    {"title": _("Ножничный подъёмник 4X"), "label": _("Четыре пары ножниц"), "url": _SCISSORS + "#seriya-4x",
     "icon": scissor_icon(4)},
    {"title": _("Четырёхстоечный подъёмник"), "label": _("Автосервис и паркинг"),
     "url": "/podemniki/chetyrehstoechnye/", "image": CATEGORIES[1]["image"]},
    {"title": _("Автомобильный подъёмник"), "label": _("Между уровнями паркинга"),
     "url": "/podemniki/avtomobilnye/", "image": CATEGORIES[4]["image"]},
    {"title": _("Консольный подъёмник 1L"), "label": _("Грузы между этажами"),
     "url": "/podemniki/konsolnye/", "image": CATEGORIES[5]["image"]},
    {"title": _("Подъёмник для мусорных контейнеров"), "label": _("Подземные площадки"),
     "url": "/podemniki/dlya-musornyh-kontejnerov/", "image": CATEGORIES[2]["image"]},
    {"title": _("Окрасочная платформа 1X"), "label": _("Для окрасочных камер"), "url": _PAINT + "#seriya-1x",
     "image": PAINT_1X},
    {"title": _("Окрасочная платформа 2D"), "label": _("Для окрасочных камер"), "url": _PAINT + "#seriya-2d",
     "image": PAINT_2D},
]
