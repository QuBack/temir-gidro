# Temir-Gidro — стек и устройство проекта

Статус: утверждено 2026-09-29.

## Стек

| Слой | Выбор | Почему |
|---|---|---|
| Backend | **Django 6.1** (Python 3.12+) | Готовая админка, sitemap, i18n, CSRF, формы, CSP — всё встроено |
| БД | **PostgreSQL 17** (локально без Docker — SQLite) | |
| Шаблоны | Django templates, серверный рендер | Весь контент в HTML сразу — идеально для Яндекса и Google |
| CSS / JS | Свой CSS, ванильный JS только для улучшений | Минимум веса → Core Web Vitals |
| Статика | WhiteNoise: хэши в именах + brotli/gzip, кэш на год | |
| Веб-сервер | **Caddy** (HTTPS автоматически, zstd/gzip, www → без www) + Gunicorn | |
| Деплой | Docker Compose | |
| Уведомления | Telegram-бот | |
| Аналитика | Яндекс.Метрика (загружается после `load`) | |

Redis не нужен: лимит заявок хранится в кэше Django на PostgreSQL.

## Структура

```
config/            настройки (всё через .env), urls
apps/core/         страницы, SEO: canonical, hreflang, JSON-LD, robots.txt, sitemap
  company.py       ⚠ данные компании (NAP) — единый источник для сайта и schema.org
  mixins.py        SeoMixin (title/description/noindex), BreadcrumbsMixin
apps/leads/        заявки: модель, форма с антиспамом, UTM, Telegram, админка
templates/         base.html + includes/ + страницы
static/            css, js, img
locale/            переводы (.po)
deploy/            Caddyfile, compose-оверлей для прода
tests/             pytest
```

## SEO: что уже реализовано

- Canonical на каждой странице, всегда от `SITE_URL` (не от заголовка Host), без query-строки.
- hreflang + x-default в `<head>` и в sitemap.xml — автоматически для всех опубликованных языков.
- `robots.txt`: `Clean-param` для Яндекса (utm, yclid, gclid), ссылка на sitemap.
- `SEO_INDEXING=False` для тестового сервера: закрывает весь сайт (robots + noindex).
- Служебные страницы (форма, «спасибо», 404) — `noindex, follow`, без canonical, не в sitemap.
- JSON-LD: `LocalBusiness` на главной, `BreadcrumbList` на внутренних.
- Open Graph; `og:image` выводится только если задан.
- Верификация Яндекс.Вебмастера и Google Search Console через `.env`.
- ETag → ответы 304 (рекомендация Яндекса).
- Слэш в конце URL обязателен, без слэша — 301.
- www → без www, http → https — 301 в Caddy.

## Мультиязычность

- Русский — в корне (`/`), остальные — с префиксом (`/kk/`, `/en/` …).
- Слаги URL переводятся: `path(_("politika-konfidencialnosti/"), …)` → перевод в `locale/<lang>/LC_MESSAGES/django.po`.
- Язык публикуется, только когда он указан в `SITE_LANGUAGES` в `.env`. Недопереведённую версию не включаем: поисковики посчитают её дублем.
- Подготовлены: `ru, kk, ky, uz, en` (список в `AVAILABLE_LANGUAGES`).
- Для контента из БД (каталог) — `django-modeltranslation`, подключим вместе с каталогом.

Добавить язык:
```
python manage.py makemessages -l kk      # нужен GNU gettext
# перевести locale/kk/LC_MESSAGES/django.po
python manage.py compilemessages
# SITE_LANGUAGES=ru,kk в .env
```

## Форма заявки

- Работает без JS (POST → редирект на `/zayavka/spasibo/`), с JS — отправка без перезагрузки.
- Антиспам без капчи: honeypot, подписанная метка времени (быстрее 3 с — бот), лимит 5 заявок / 10 мин с одного IP.
- Подозрительные заявки **не теряются**: сохраняются со статусом «спам» и в Telegram не уходят.
- Сохраняются UTM-метки (первое касание), внешний источник перехода, страница входа, страница отправки.
- Цели Метрики: `lead_sent`, `phone_click`, `email_click`.

## Админка

По пути из `ADMIN_URL`. Заявки: статусы, фильтры, поиск, заметки, массовые действия, выгрузка в CSV для Excel (с защитой от формул). Спам по умолчанию скрыт.

## Запуск

Локально:
```
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
copy .env.example .env          # вписать SECRET_KEY
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createcachetable
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver
.venv\Scripts\python -m pytest
```

Весь стек в Docker: `docker compose up --build`.

Прод: `SITE_DOMAIN=temir-gidro.kz docker compose -f compose.yml -f deploy/compose.prod.yml up -d --build`.

## Ещё не сделано (следующие этапы)

- Изображения: AVIF/WebP, srcset, шаблонный тег `{% picture %}` — вместе с каталогом (зависит от того, грузятся ли фото через админку).
- Каталог / услуги — после утверждения структуры сайта.
- Дизайн — через скилл frontend-design, после брифа.
- Данные компании в `apps/core/company.py`, текст политики конфиденциальности.
- favicon.ico, web manifest, дефолтная OG-картинка — вместе с дизайном.
- Бэкапы БД и медиа, мониторинг — к запуску.
- HSTS preload — осознанно выключен, решим к запуску.
