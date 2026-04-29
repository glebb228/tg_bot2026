from aiogram import Bot, Dispatcher

from src.bot.config import load_config
from src.bot.database.session import create_db, session_manager
from src.bot.handlers.callbacks import callbacks_router
from src.bot.handlers.start import start_router


def main() -> None:
    config = load_config()
    create_db(config.database_url)

    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher()

    dispatcher["session_manager"] = session_manager
    dispatcher.include_router(start_router)
    dispatcher.include_router(callbacks_router)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
