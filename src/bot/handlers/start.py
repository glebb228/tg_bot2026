from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.constants import MAIN_MENU_TEXT, WELCOME_TEXT
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.services.users import get_or_create_user


start_router = Router()


@start_router.message(CommandStart())
async def handle_start(message: Message, session_manager) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    with session_manager() as session:
        _, created = get_or_create_user(session, telegram_user)

    greeting_suffix = "Ты успешно зарегистрирован в системе." if created else "С возвращением!"

    await message.answer(WELCOME_TEXT)
    await message.answer(
        f"{greeting_suffix}\n\n{MAIN_MENU_TEXT}",
        reply_markup=get_main_menu_keyboard(),
    )
