# temir-gidro

Сайт ТЕМИР ГИДРО на Django. Требования — `docs/01-requirements.md`, стек — `docs/02-stack.md`.

## Локальный запуск

```sh
uv venv .venv
uv pip install -p .venv -r requirements-dev.txt
cp .env.example .env
.venv/Scripts/python manage.py migrate          # на Linux/macOS: .venv/bin/python
.venv/Scripts/python manage.py createsuperuser  # логин и пароль для админки
.venv/Scripts/python manage.py runserver
```

Тесты: `.venv/Scripts/python -m pytest`.

## Заявки

Формы на сайте сохраняют заявки в базу. Смотреть их — в админке: `http://127.0.0.1:8000/admin/` → «Заявки»
(путь задаётся `ADMIN_URL` в `.env`). Там же статусы («Новая», «В работе», «Закрыта»), заметки менеджера
и выгрузка в CSV для Excel. Подозрительные заявки не теряются: они получают статус «Спам» и скрыты из списка,
пока не выбран фильтр по этому статусу.

Уведомления о новых заявках в Telegram: создать бота у @BotFather и заполнить в `.env`
`TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`. Без них заявки просто сохраняются в базу.

## Установка на сервер

Нужен чистый сервер с Ubuntu 22.04/24.04 или Debian 12 (от 1 ГБ памяти, лучше 2 ГБ) и доступ по SSH под root
или пользователем с sudo. Скрипт сам ставит Docker, скачивает код, генерирует пароли в `.env`,
собирает и запускает сайт (Django + PostgreSQL + Caddy).

```sh
# Показать результат по IP сервера (http, сайт закрыт от поисковиков):
curl -fsSL https://raw.githubusercontent.com/QuBack/temir-gidro/main/deploy/install.sh | sudo bash

# С доменом: сначала A-запись домена (и www) на IP сервера, потом
git clone https://github.com/QuBack/temir-gidro.git /opt/temir-gidro
sudo bash /opt/temir-gidro/deploy/install.sh --domain temir-gidro.com
# Тестовый поддомен, закрытый от индексации: добавить --staging
```

Если порт 80 или 443 уже занят другой программой (nginx, apache), скрипт покажет, какой именно.
Для показа по IP 443 не нужен; если занят и 80 — `sudo bash deploy/install.sh --port 8080`
(сайт будет на `http://IP:8080/`).

В конце скрипт печатает адрес сайта и адрес админки. Пользователь для админки:

```sh
cd /opt/temir-gidro
sudo docker compose -f compose.yml -f deploy/compose.prod.yml exec web python manage.py createsuperuser
```

- Обновить сайт после изменений в репозитории: `sudo bash /opt/temir-gidro/deploy/update.sh`
  (сначала делает бэкап базы).
- Бэкап базы с заявками: `sudo bash /opt/temir-gidro/deploy/backup.sh` → `backups/`. Ежедневно —
  строка для crontab в начале `deploy/backup.sh`.
- Настройки (Метрика, Telegram, верификация поисковиков) — в `/opt/temir-gidro/.env`, после правки
  `sudo bash deploy/update.sh`.
- Перешли с IP на домен: удалить `.env` нельзя (там пароль базы) — поменять в нём `SITE_DOMAIN`, `SITE_URL`,
  `ALLOWED_HOSTS`, `HTTPS=True`, `CADDYFILE=deploy/Caddyfile`, `SEO_INDEXING=True` и запустить `update.sh`.
