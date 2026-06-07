from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.constants import MAIN_MENU_TEXT, WELCOME_TEXT
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.keyboards.settings import get_initial_language_keyboard
from src.bot.services.learning import create_custom_word_for_user
from src.bot.services.users import get_or_create_user
from src.bot.states import AddWordState


start_router = Router()


@start_router.message(CommandStart())
async def handle_start(message: Message, session_manager) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    with session_manager() as session:
        _, created = get_or_create_user(session, telegram_user)

    await message.answer(WELCOME_TEXT)
    if created:
        await message.answer(
            "Выбери язык, который хочешь изучать.",
            reply_markup=get_initial_language_keyboard(),
        )
        return

    await message.answer(
        f"С возвращением!\n\n{MAIN_MENU_TEXT}",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.message(Command("menu"))
async def handle_menu(message: Message) -> None:
    await message.answer(MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())


@start_router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Как пользоваться ботом\n\n"
        "/start — регистрация и запуск\n"
        "/menu — открыть главное меню\n"
        "/help — показать эту справку\n\n"
        "Основные разделы:\n"
        "Начать урок — карточки слов по уровню.\n"
        "Тренировка — тесты, режим до первой ошибки и повторение ошибок.\n"
        "Тема дня — случайная тема для короткой практики.\n"
        "Мой словарь — сохраненные и вручную добавленные слова.\n"
        "Прогресс — статистика, цель дня и слабые слова.\n"
        "Настройки — язык, уровень и напоминания.",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.message(Command("cancel"))
async def handle_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=get_main_menu_keyboard())


@start_router.message(AddWordState.waiting_for_word)
async def handle_custom_word(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Напиши слово текстом или отправь /cancel для отмены.")
        return

    await state.update_data(foreign_word=text)
    await state.set_state(AddWordState.waiting_for_translation)
    await message.answer("Теперь напиши перевод этого слова.")


@start_router.message(AddWordState.waiting_for_translation)
async def handle_custom_translation(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Напиши перевод текстом или отправь /cancel для отмены.")
        return

    await state.update_data(translation=text)
    await state.set_state(AddWordState.waiting_for_example)
    await message.answer("Добавь пример предложения. Если пример не нужен, напиши «-».")


@start_router.message(AddWordState.waiting_for_example)
async def handle_custom_example(message: Message, state: FSMContext, session_manager) -> None:
    if message.from_user is None:
        await message.answer("Не удалось определить пользователя Telegram.")
        return

    text = (message.text or "").strip()
    data = await state.get_data()
    example = "" if text == "-" else text

    with session_manager() as session:
        saved = create_custom_word_for_user(
            session,
            message.from_user.id,
            data["foreign_word"],
            data["translation"],
            example,
        )

    await state.clear()
    if not saved:
        await message.answer("Не удалось сохранить слово. Нажми /start и попробуй еще раз.")
        return

    await message.answer(
        "Слово сохранено в словарь.",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.message()
async def handle_unexpected_text(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is not None:
        await message.answer("Заверши текущее действие или отправь /cancel.")
        return

    await message.answer(
        "Сейчас бот работает через кнопки. Выбери нужный раздел в меню ниже.",
        reply_markup=get_main_menu_keyboard(),
    )
