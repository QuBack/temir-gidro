# План действий — temir-gidro.ru

## Critical — сразу

1. **Проверить, что KillBot пропускает поисковых роботов.**
   - Яндекс.Вебмастер → Инструменты → «Проверка ответа сервера» для `/`, `/robots.txt`,
     `/sitemap_index.xml`: должен быть реальный контент, а не страница проверки.
   - Вебмастер → Индексирование → «Анализ robots.txt»: Яндекс должен видеть ваши правила.
   - Google Search Console → «Проверка URL» → «Проверить страницу на сайте» → скриншот/HTML.
   - В настройках KillBot: белый список Yandex/Google/Bing (по reverse DNS), исключить из
     проверки `/robots.txt`, `/sitemap*.xml`, `/favicon.ico`, IndexNow-ключ.
2. **Редиректы 301 при переезде на Django** (сейчас их нет):

   | Старый URL (WordPress) | Новый URL (Django) |
   |---|---|
   | `/equipment/` | `/podemniki/` |
   | `/equipment/temir-gidro-1x/` | `/podemniki/nozhnichnye/#seriya-1x` → лучше `/podemniki/nozhnichnye/` |
   | `/equipment/temir-gidro-x2/` | `/podemniki/nozhnichnye/` |
   | `/equipment/temir-gidro-3x/` | `/podemniki/nozhnichnye/` |
   | `/equipment/temir-gidro-4x/` | `/podemniki/nozhnichnye/` |
   | `/equipment/temir-gidro-console/` | `/podemniki/konsolnye/` |
   | `/equipment/auto-lifts/` | `/podemniki/chetyrehstoechnye/` |
   | `/equipment/transport-lift/` | `/podemniki/avtomobilnye/` |
   | `/equipment/waste-container-lifter/` | `/podemniki/dlya-musornyh-kontejnerov/` |
   | `/equipment/podemniki-dlya-okrasochnyh-kamer/` | `/podemniki/dlya-okrasochnyh-kamer/` |
   | `/equipment/подъемники-для-окрасочных-камер-2d/` | `/podemniki/dlya-okrasochnyh-kamer/` |
   | `/accessories/gidraulic-cylinders/` | `/gidrocilindry/` |
   | `/about-us/` | `/o-kompanii/` |
   | `/order/` | `/zayavka/` |
   | `/blog/` и статьи | `/stati/…` (сопоставить по списку статей) |
   | `/feed/`, `/comments/feed/`, `/wp-json/*` | 410 Gone |

   Полный список старых URL взять из Вебмастера («Страницы в поиске») — меню даёт не все.
   Внимание: в Django часть страниц (`/podemniki/chetyrehstoechnye/`, `/gidrocilindry/` и др.)
   ещё не сделана — редирект на 404 хуже, чем отсутствие переезда.

## High — 1–2 недели (на старом сайте, если переезд не завтра)

3. Прописать meta description главной и ключевых страниц в Yoast.
4. Убрать «Компания ПРОМСПЕЦМЕТ» из первого абзаца/og:description или пояснить связь брендов.
5. Коммерческие факторы на сайте: адрес производства, реквизиты, «цена от …», доставка по
   регионам, гарантия, мессенджеры, карта. Завести/заполнить карточку в Яндекс Бизнесе.
6. Наполнить главную: 300–600 слов фактов — сроки, объёмы, грузоподъёмность, объекты, фото цеха.

## Medium — месяц

7. Фото моделей — тегами `<img>` с alt вместо CSS-фона; WebP/AVIF вместо PNG.
8. Отключить WooCommerce и неиспользуемые плагины Elementor (−скрипты, быстрее LCP).
9. Определиться с политикой ИИ-краулеров в KillBot (YandexAdditional, GoogleOther и т.д.),
   если нужна видимость в Алисе AI / AI Overviews.
10. Получить ключ Google PageSpeed API (бесплатно) — для замеров Core Web Vitals.

## Low

11. Привести заголовки к иерархии (CTA — не H3, бренд в футере — не H2).
12. Опечатки в названиях карточек, имя файла логотипа `temir-girdo-logo`.

## Чтобы довести аудит до полного

- Добавить ваш IP в белый список KillBot на время аудита — тогда можно обойти все страницы
  (по-прежнему медленно, 1 запрос в 5–8 секунд), **или**
- прислать выгрузки из Вебмастера («Страницы в поиске», «Поисковые запросы», «Диагностика»), **или**
- провести аудит нового Django-сайта локально — без KillBot и без риска.
