# Telegram Bot for Language Learning

Учебный MVP Telegram-бота для изучения иностранной лексики. Бот помогает пользователю изучать слова по темам, сохранять личный словарь, проходить тренировки, отслеживать прогресс и настраивать напоминания.

## Возможности

- регистрация пользователя через `/start` с выбором языка при первом запуске;
- главное меню с разделами обучения, тренировки, словаря, прогресса и настроек;
- поддержка английского, испанского и итальянского языков;
- 45 учебных тем и 396 карточек на каждый язык;
- фильтрация тем по уровню пользователя: A1, A2, B1, B2;
- отдельный прогресс и словарь для каждого выбранного языка;
- рекомендованные карточки: новые, слабые или случайные;
- личный словарь пользователя;
- ручное добавление слова, перевода и примера;
- удаление слов из словаря;
- тест по словам из словаря до 10 случайных карточек за попытку;
- обычный тест по выбранной теме;
- режим `До первой ошибки` со случайными словами из доступных уровней;
- режим `Повторить ошибки` по слабым словам пользователя;
- режим вызова выше текущего уровня с предложением повысить уровень;
- сохранение прогресса по словам и попыткам тестов;
- экран статистики с целью дня, точностью, сильной темой и темой для повторения;
- настройка языка, уровня и локальных напоминаний;
- команды `/menu`, `/help`, `/cancel`;
- обработка текстовых сообщений вместо кнопок.

## Стек

- Python 3.11+
- aiogram 3
- SQLAlchemy 2
- PostgreSQL через `psycopg`
- SQLite как локальный fallback
- python-dotenv

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
│       ├── states.py
│       ├── database/
│       │   ├── base.py
│       │   ├── models.py
│       │   └── session.py
│       ├── handlers/
│       │   ├── callbacks.py
│       │   └── start.py
│       ├── keyboards/
│       │   ├── learning.py
│       │   ├── main_menu.py
│       │   └── settings.py
│       └── services/
│           ├── learning.py
│           ├── reminders.py
│           ├── settings.py
│           └── users.py
├── requirements.txt
└── README.md
```

## Запуск

1. Создать виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Создать файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/tg_bot2026
```

Для локальной проверки без PostgreSQL можно использовать SQLite:

```env
DATABASE_URL=sqlite:///bot.sqlite3
```

4. Запустить бота:

```bash
python3 -m src.main
```

При первом запуске приложение создает таблицы и заполняет учебные темы карточками.

## Основные модули

- [src/main.py](/Users/glebkozlov/Desktop/tg_bot2026/src/main.py) — запуск бота, polling и фоновых напоминаний.
- [src/bot/config.py](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/config.py) — загрузка переменных окружения.
- [src/bot/database/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/database) — модели и настройка БД.
- [src/bot/handlers/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/handlers) — обработчики команд, сообщений и callback-кнопок.
- [src/bot/keyboards/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/keyboards) — inline-клавиатуры.
- [src/bot/services/](/Users/glebkozlov/Desktop/tg_bot2026/src/bot/services) — бизнес-логика обучения, словаря, прогресса, настроек и напоминаний.

## Ограничения MVP

- напоминания отправляются только пока бот запущен;
- постоянный аптайм будет обеспечен после деплоя на сервер;
- миграции реализованы простым способом через проверку колонок, для промышленной версии лучше подключить Alembic;
- API внешнего переводчика не используется, так как в MVP применяются готовые наборы слов.

## Документация

- [Архитектура](docs/architecture.md)
- [Схема БД](docs/db_schema.md)
- [User Flow](docs/user_flow.md)
