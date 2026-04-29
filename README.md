# Telegram Bot for Language Learning

Учебный проект Telegram-бота для изучения иностранных языков. На текущем этапе реализованы базовая архитектура приложения, подключение к базе данных, регистрация пользователя и навигация по основным разделам.

## Возможности

- обработка команды `/start`
- регистрация нового пользователя в базе данных
- отображение главного меню
- переходы между разделами через inline-кнопки
- документация по архитектуре, базе данных и сценариям взаимодействия

## Стек

- Python 3.11+
- aiogram 3
- SQLAlchemy 2
- SQLite

## Структура проекта

```text
.
├── docs/
│   ├── architecture.md
│   ├── db_schema.md
│   └── user_flow.md
├── src/
│   ├── main.py
│   └── bot/
│       ├── config.py
│       ├── constants.py
│       ├── database/
│       │   ├── base.py
│       │   ├── models.py
│       │   └── session.py
│       ├── handlers/
│       │   ├── callbacks.py
│       │   └── start.py
│       ├── keyboards/
│       │   └── main_menu.py
│       └── services/
│           └── users.py
```

## Запуск

1. Создайте виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=sqlite:///bot.sqlite3
```

4. Запустите бота:

```bash
python3 -m src.main
```

После запуска приложение автоматически создаст локальную базу `bot.sqlite3`.

## Основные модули

- [src/main.py](/Users/glebkozlov/Desktop/tg_bot2026/src/main.py) — точка входа и запуск бота
- [src/bot/config.py](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/config.py) — загрузка конфигурации
- [src/bot/database/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/database) — модели и настройка базы данных
- [src/bot/handlers/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/handlers) — обработчики команд и callback-событий
- [src/bot/keyboards/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/keyboards) — клавиатуры меню
- [src/bot/services/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/services) — логика работы с пользователями

## Документация

- [Архитектура](docs/architecture.md)
- [Схема БД](docs/db_schema.md)
- [User Flow](docs/user_flow.md)
