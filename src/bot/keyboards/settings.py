from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Язык", callback_data="settings:open:language")],
            [InlineKeyboardButton(text="Уровень", callback_data="settings:open:level")],
            [InlineKeyboardButton(text="Напоминания", callback_data="settings:open:reminders")],
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")],
        ]
    )


def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Английский", callback_data="settings:set:language:English")],
            [InlineKeyboardButton(text="Испанский", callback_data="settings:set:language:Spanish")],
            [InlineKeyboardButton(text="Итальянский", callback_data="settings:set:language:Italian")],
            [InlineKeyboardButton(text="Назад к настройкам", callback_data="section:settings")],
        ]
    )


def get_initial_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Английский", callback_data="onboarding:language:English")],
            [InlineKeyboardButton(text="Испанский", callback_data="onboarding:language:Spanish")],
            [InlineKeyboardButton(text="Итальянский", callback_data="onboarding:language:Italian")],
        ]
    )


def get_level_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="A1", callback_data="settings:set:level:A1")],
            [InlineKeyboardButton(text="A2", callback_data="settings:set:level:A2")],
            [InlineKeyboardButton(text="B1", callback_data="settings:set:level:B1")],
            [InlineKeyboardButton(text="B2", callback_data="settings:set:level:B2")],
            [InlineKeyboardButton(text="Назад к настройкам", callback_data="section:settings")],
        ]
    )


def get_reminder_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Включить на 09:00", callback_data="settings:set:reminders:09:00")],
            [InlineKeyboardButton(text="Включить на 18:00", callback_data="settings:set:reminders:18:00")],
            [InlineKeyboardButton(text="Включить на 21:00", callback_data="settings:set:reminders:21:00")],
            [InlineKeyboardButton(text="Выключить", callback_data="settings:set:reminders:off")],
            [InlineKeyboardButton(text="Назад к настройкам", callback_data="section:settings")],
        ]
    )
