from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.bot.constants import MAIN_MENU_TEXT, SECTION_TEXTS
from src.bot.keyboards.main_menu import (
    get_back_to_menu_keyboard,
    get_main_menu_keyboard,
)


callbacks_router = Router()


@callbacks_router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("section:"))
async def open_section(callback: CallbackQuery) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    section_key = callback.data.split(":", maxsplit=1)[1]
    section_text = SECTION_TEXTS.get(section_key, "Раздел пока недоступен.")

    await callback.message.edit_text(
        section_text,
        reply_markup=get_back_to_menu_keyboard(),
    )
    await callback.answer()
