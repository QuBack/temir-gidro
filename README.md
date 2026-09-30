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
