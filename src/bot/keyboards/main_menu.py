from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать урок", callback_data="section:lessons")],
            [InlineKeyboardButton(text="Мой словарь", callback_data="section:dictionary")],
            [InlineKeyboardButton(text="Прогресс", callback_data="section:progress")],
            [InlineKeyboardButton(text="Настройки", callback_data="section:settings")],
        ]
    )


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")],
        ]
    )

