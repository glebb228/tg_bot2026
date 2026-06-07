import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.config import load_config
from src.bot.database.session import create_db, session_manager
from src.bot.handlers.callbacks import callbacks_router
from src.bot.handlers.start import start_router
from src.bot.services.reminders import run_reminder_scheduler


async def main() -> None:
    config = load_config()
    create_db(config.database_url)

    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())

    dispatcher["session_manager"] = session_manager
    dispatcher.include_router(start_router)
    dispatcher.include_router(callbacks_router)

    reminder_task = asyncio.create_task(run_reminder_scheduler(bot, session_manager))
    try:
        await dispatcher.start_polling(bot)
    finally:
        reminder_task.cancel()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
