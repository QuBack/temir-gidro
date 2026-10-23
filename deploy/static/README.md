# Сайт на виртуальном хостинге без Python (Timeweb)

На хостинге с PHP, но без Docker и нового Python сайт работает как набор готовых HTML-страниц.
Конфигураторы, 3D, фото, редиректы со старого сайта работают; заявки уходят письмом через PHP
(`send.php`) и копией пишутся в `~/temir-gidro/leads.csv`. Нет админки, заявок в базе и Telegram.

## Собрать (на своём компьютере)

```sh
DEBUG=False SITE_URL=https://temir-gidro.ru SEO_INDEXING=True ALLOWED_HOSTS=temir-gidro.ru \
  .venv/Scripts/python manage.py export_static dist
```

Счётчик Метрики и коды верификации берутся из переменных `YANDEX_METRIKA_ID`, `YANDEX_VERIFICATION`,
`GOOGLE_VERIFICATION` — добавьте их в команду. Затем заархивируйте содержимое `dist/` (вместе с `.htaccess`).

## Залить

1. Файловый менеджер Timeweb: архив в `~/temir-gidro/`, очистить `public_html`, распаковать архив в `public_html`.
2. Почта — файл `~/temir-gidro/lead-config.php` (рядом с `public_html`, не внутри):
   ```php
   <?php return ['to' => 'seo@temir.ru', 'smtp_user' => 'seo@temir.ru', 'smtp_password' => 'ПАРОЛЬ_ПРИЛОЖЕНИЯ'];
   ```
3. Панель Timeweb → сайт → SSL: выпустить Let's Encrypt и включить перенаправление на HTTPS.

После любой правки сайта — собрать заново и перезалить `public_html` (файл `lead-config.php` и `leads.csv` не трогать).
