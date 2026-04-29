# Telegram Bot MVP for Language Learning

MVP Telegram-бота для изучения иностранных языков. Проект реализует результаты спринтов 1 и 2:

- выбраны Python и библиотека `aiogram`;
- спроектирована схема БД и полная детальная схема диалогов;
- реализовано подключение к БД;
- добавлена команда `/start`;
- новый пользователь сохраняется в БД;
- настроено главное меню и навигация по разделам-заглушкам.

## Стек

- Python 3.11+
- aiogram 3
- SQLAlchemy 2
- SQLite

## Структура

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

## Быстрый старт

1. Создайте виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Подготовьте переменные окружения:

```bash
cp .env.example .env
```

4. Укажите токен от `@BotFather` в `.env`.

5. Запустите бота:

```bash
python -m src.main
```

## Что уже умеет бот

- отвечает на `/start`;
- регистрирует пользователя в БД при первом входе;
- показывает главное меню;
- позволяет перемещаться по разделам через inline-кнопки;
- отдает заглушки для будущих модулей: уроки, словарь, прогресс, настройки.

## Что относится к спринту 1

- в [user_flow.md](/Users/glebkozlov/Desktop/tg_bot2026/docs/user_flow.md) описана полная схема диалогов целевого бота;
- в коде осознанно оставлены заглушки разделов, потому что по спринту 2 реализуется только ядро, БД, `/start` и навигация.

## Документация по спринтам

- [Архитектура](docs/architecture.md)
- [Схема БД](docs/db_schema.md)
- [User Flow](docs/user_flow.md)
