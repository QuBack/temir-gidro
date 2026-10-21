"""Hydraulic power units page: /gidrostancii/ (mockup docs/mockups/gidrostancii-maket.html).

TODO: every figure here is a placeholder until the client sends real data (2026-10): the ranges,
the types and their specs, the motor and tank series, the lead times. Pictures are generated
(Codex, 2026) until real photos come.
"""

from django.utils.translation import gettext_lazy as _

from .catalog import CATEGORIES, CYLINDERS, FAQ, img


def _photo(name):
    return img(f"power-units/{name}", (1200, 900), widths=(400, 800, 1200))


HERO = img("power-units/gidrostanciya-380v", (1254, 1254), widths=(200, 400, 800, 1254))
HERO_SIDE = img("power-units/gidrostanciya-380v-sboku", (1254, 1254), widths=(200, 800, 1254))

PAGE = {
    "title": _("Гидростанции на заказ"),
    "seo_title": _("Гидростанции (маслостанции) на заказ от производителя | ТЕМИР ГИДРО"),
    "seo_description": _(
        "Гидростанции для подъёмников, гидроцилиндров, прессов и станков: подбор насоса, мотора и бака "
        "по давлению и скорости, сборка и испытания на стенде. Расчёт за 24 часа."
    ),
    "lead": _(
        "Собираем маслостанции под ваш гидроцилиндр, подъёмник или пресс: подбираем насос, мотор и бак "
        "по давлению и скорости, испытываем на стенде."
    ),
    "image": HERO,
    "image_alt": _("Гидростанция ТЕМИР ГИДРО на 380 В: бак, электродвигатель, клапанный блок"),
    # Other views beside the render on the first screen (as on the console lift).
    "views": [(HERO_SIDE, _("Гидростанция ТЕМИР ГИДРО — вид сбоку"))],
    # Key figures under the first screen: (value, unit, label).
    "facts": [
        (_("до 32"), _("МПа"), _("давление")),
        ("0,37–30", _("кВт"), _("мотор")),
        ("5–400", _("л"), _("бак")),
        ("220 / 380", _("В"), _("питание")),
        ("24", _("ч"), _("расчёт")),
    ],
    # (key, label): the purposes, as chips that filter the types below.
    "purposes": [
        ("lift", _("Подъёмники и платформы")),
        ("cylinder", _("Гидроцилиндры")),
        ("press", _("Прессы")),
        ("machine", _("Станки")),
        ("mobile", _("Выездные работы")),
        ("stand", _("Испытательные стенды")),
    ],
    # (title, text, image, [(label, value)], purposes)
    "types": [
        (
            _("Компактные"),
            _("Для подъёмных столов, рамп и небольших прессов. Встраиваются прямо в оборудование."),
            img("power-units/kompaktnaya", (800, 600), widths=(400, 800)),
            [(_("Давление"), _("до 21 МПа")), (_("Бак"), _("1–20 л"))],
            ["lift", "press", "cylinder"],
        ),
        (
            _("Промышленные"),
            _("Для подъёмников, ножничных столов и стационарного оборудования: 380 В, вертикальный мотор."),
            img("power-units/promyshlennaya", (800, 600), widths=(400, 800)),
            [(_("Давление"), _("до 25 МПа")), (_("Бак"), _("20–200 л"))],
            ["lift", "cylinder", "machine"],
        ),
        (
            _("Высокого давления"),
            _("Для прессов, испытательных стендов и мощных цилиндров: аксиально-поршневой насос, охладитель."),
            img("power-units/vysokogo-davleniya", (800, 600), widths=(400, 800)),
            [(_("Давление"), _("до 32 МПа")), (_("Мотор"), _("до 30 кВт"))],
            ["press", "stand", "cylinder"],
        ),
        (
            _("С ручным насосом"),
            _("Ручной дублёр опустит платформу, если пропало питание: для подъёмников и лифтов."),
            img("power-units/s-ruchnym-nasosom", (800, 600), widths=(400, 800)),
            [(_("Привод"), _("эл. + ручной")), (_("Для"), _("подъёмников"))],
            ["lift"],
        ),
        (
            _("Мобильные"),
            _("На тележке с колёсами и быстроразъёмными рукавами: переезжают между объектами и стендами."),
            img("power-units/mobilnaya", (800, 600), widths=(400, 800)),
            [(_("Бак"), _("10–60 л")), (_("Питание"), _("220 / 380 В"))],
            ["mobile", "stand", "cylinder"],
        ),
        (
            _("С автоматикой"),
            _("Шкаф управления, датчики давления и уровня, пульт или управление от вашего ПЛК."),
            img("power-units/promyshlennaya", (800, 600), widths=(400, 800)),
            [(_("Управление"), _("пульт / ПЛК")), (_("Датчики"), _("по ТЗ"))],
            ["machine", "press", "stand"],
        ),
    ],
    # The kit on the industrial unit with callouts, as on the lift model pages:
    # (kit item index, x %, y %) on the picture.
    "kit_image": HERO,
    "kit_markers": [(0, 25, 76), (1, 30, 24), (2, 30, 47), (3, 55, 44), (4, 86, 42), (5, 74, 33)],
    "kit": [
        (
            _("Бак"),
            _("Объём — около трёх минутных подач насоса: масло успевает остыть и отстояться."),
            "kit-power-unit",
        ),
        (_("Электродвигатель"), _("220 или 380 В; мощность считаем по давлению и расходу."), "cog"),
        (_("Насос"), _("Шестерённый или аксиально-поршневой: задаёт скорость цилиндра."), "kit-speed"),
        (_("Клапанный блок"), _("Предохранительный и обратный клапаны, распределитель."), "kit-valve"),
        (_("Фильтр и сапун"), _("Держат масло чистым — от этого зависит ресурс уплотнений."), "kit-overload"),
        (_("Манометр и датчики"), _("Показывают давление и уровень масла; датчики — по запросу."), "gauge"),
    ],
    # Where our units work: our own equipment, the units come with it.
    "uses": [
        (CATEGORIES[0]["title"], CATEGORIES[0]["url"], CATEGORIES[0]["image"]),
        (CATEGORIES[5]["title"], CATEGORIES[5]["url"], CATEGORIES[5]["image"]),
        (CATEGORIES[3]["title"], CATEGORIES[3]["url"], CATEGORIES[3]["image"]),
        (_("Гидроцилиндры"), CYLINDERS["url"], CYLINDERS["image"]),
    ],
    # (title, text, icon) — the production route.
    "steps": [
        (_("Опросный лист"), _("Или ТЗ, чертёж, параметры цилиндра."), "clipboard-pen"),
        (_("Расчёт"), _("Насос, мотор, бак и смета — за сутки."), "calculator"),
        (_("Гидросхема"), _("Согласуем схему и компоновку с вами."), "drafting-compass"),
        (_("Сборка"), _("На нашем участке, из проверенных комплектующих."), "cog"),
        (_("Испытания"), _("Стенд, настройка предохранительного клапана, проверка герметичности."), "gauge"),
        (_("Отгрузка"), _("С паспортом и гидросхемой, в любой регион."), "truck"),
    ],
    "photos": [
        (_photo("sborka"), _("Сборка гидростанции на участке")),
        (_photo("ispytaniya"), _("Испытания гидростанции на стенде")),
        (_photo("u-podemnika"), _("Гидростанция у ножничного подъёмника")),
        (_photo("klapannyj-blok"), _("Клапанный блок гидростанции")),
        (_photo("gotovye-k-otgruzke"), _("Гидростанции перед отгрузкой")),
    ],
    # What the questionnaire asks; the PDF is in static/docs/.
    "questionnaire": [
        _("Что приводит станция и сколько цилиндров"),
        _("Нагрузка, ход и скорость"),
        _("Питание и режим работы"),
        _("Место установки и климат"),
    ],
    "questionnaire_pdf": "docs/oprosnyj-list-gidrostanciya-temir-gidro.pdf",
    # What to write in the lead form.
    "lead_params": [
        ("F", _("нагрузку или усилие цилиндра")),
        ("v", _("скорость или время подъёма")),
        ("U", _("питание: 220 или 380 В")),
        (_("Где"), _("что приводит станция и где стоит")),
    ],
    "faq": [
        (
            _("Какую гидростанцию выбрать для подъёмника?"),
            _(
                "Её определяют нагрузка, ход и время подъёма: от них зависят давление, подача насоса и мощность "
                "мотора. Посчитайте в подборе на этой странице или пришлите параметры — подберём сами."
            ),
        ),
        (
            _("Можно заменить станцию на подъёмнике другого производителя?"),
            _(
                "Да. Пришлите фото таблички старой станции и параметры подъёмника — соберём совместимую по "
                "давлению, подаче и присоединению рукавов."
            ),
        ),
        (
            _("Какое масло заливать и как часто менять?"),
            _(
                "Обычно минеральное гидравлическое масло ISO VG 32 или 46 — точную марку укажем в паспорте. "
                "Менять — по паспорту, как правило раз в год или по наработке."
            ),
        ),
        (
            _("Сколько стоит гидростанция?"),
            _(
                "Цена зависит от давления, подачи, мотора и автоматики. Пришлите параметры или опросный лист — "
                "рассчитаем стоимость и сроки в течение суток."
            ),
        ),
        FAQ[4],
    ],
}

# Calculator (static/js/power_unit_config.js): the standard series it rounds up to.
# TODO: the client's real motor, pump and tank series and lead times.
CONFIG = {
    "bores": [32, 40, 50, 63, 80, 100, 125, 160, 200, 250],
    "motors": [0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22, 30],  # kW
    "motor_max_220": 2.2,  # single phase stops here
    "tanks": [5, 10, 20, 40, 63, 100, 160, 250, 400],  # litres
    "pressure_max": 32,  # MPa
    "gear_pump_max": 21,  # MPa: above it an axial piston pump
    "efficiency": 0.8,
    "days": [[2.2, 10], [7.5, 15], [30, 20]],  # motor kW up to → working days
    "load": {"min": 0.5, "max": 50, "step": 0.5, "value": 8},  # t
    "bore": 4,  # index: 80 mm
    "stroke": {"min": 100, "max": 5000, "step": 50, "value": 1200},  # mm
    "time": {"min": 5, "max": 120, "step": 1, "value": 25},  # s
}

# Behind the calculator and the request form (generated, Codex, 2026).
LEAD_BG = img("backgrounds/chertezh-gidrostancii-zayavka", (1920, 1080), widths=(768, 1280, 1920))
