import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.constants import MAIN_MENU_TEXT, SECTION_TEXTS
from src.bot.keyboards.learning import (
    get_card_keyboard,
    get_dictionary_quiz_keyboard,
    get_dictionary_keyboard,
    get_empty_dictionary_keyboard,
    get_quiz_keyboard,
    get_quiz_result_keyboard,
    get_survival_quiz_keyboard,
    get_training_mode_keyboard,
    get_training_sets_keyboard_for_mode,
    get_weak_quiz_keyboard,
    get_word_sets_keyboard,
)
from src.bot.keyboards.main_menu import (
    get_back_to_menu_keyboard,
    get_main_menu_keyboard,
)
from src.bot.keyboards.settings import (
    get_language_keyboard,
    get_level_keyboard,
    get_reminder_keyboard,
    get_settings_keyboard,
)
from src.bot.services.learning import (
    build_quiz_question,
    build_dictionary_quiz_question,
    build_survival_quiz_question,
    build_weak_quiz_question,
    get_card_by_position,
    get_challenge_word_sets,
    get_dictionary_card_by_position,
    get_progress_stats,
    get_random_daily_word_set,
    get_survival_word_cards,
    get_user_saved_cards,
    get_weak_word_cards,
    get_word_set_level,
    get_next_level,
    get_word_sets,
    record_word_answer_progress,
    record_quiz_attempt,
    remove_word_for_user,
    save_word_for_user,
)
from src.bot.services.settings import (
    get_user_settings,
    update_user_language,
    update_user_level,
    update_user_reminders,
)
from src.bot.states import AddWordState


callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("onboarding:language:"))
async def finish_onboarding_language(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    language = callback.data.split(":")[2]
    with session_manager() as session:
        updated = update_user_language(session, callback.from_user.id, language)

    if not updated:
        await callback.answer("Не удалось сохранить язык.", show_alert=True)
        return

    await callback.message.edit_text(
        f"Язык сохранен: {format_language_name(language)}\n\n{MAIN_MENU_TEXT}",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer("Язык выбран.")


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


@callbacks_router.callback_query(F.data == "daily:topic")
async def open_daily_topic(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None:
        await callback.answer()
        return

    with session_manager() as session:
        word_set = get_random_daily_word_set(session, callback.from_user.id)

    if word_set is None:
        await callback.answer("Не удалось подобрать тему дня.", show_alert=True)
        return

    await callback.message.edit_text(
        (
            "Тема дня\n\n"
            f"{word_set.title} ({word_set.level})\n"
            f"{word_set.description}\n\n"
            "Можно открыть рекомендованную карточку или сразу пройти тест."
        ),
        reply_markup=get_word_sets_keyboard([word_set]),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("section:"))
async def open_section(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    section_key = callback.data.split(":", maxsplit=1)[1]
    if section_key == "lessons":
        with session_manager() as session:
            word_sets = get_word_sets(session, callback.from_user.id)
        await callback.message.edit_text(
            SECTION_TEXTS["lessons"],
            reply_markup=get_word_sets_keyboard(word_sets),
        )
        await callback.answer()
        return

    if section_key == "training":
        await callback.message.edit_text(
            SECTION_TEXTS["training"],
            reply_markup=get_training_mode_keyboard(),
        )
        await callback.answer()
        return

    if section_key == "dictionary":
        with session_manager() as session:
            saved_cards = get_user_saved_cards(session, callback.from_user.id)

        if not saved_cards:
            await callback.message.edit_text(
                "Словарь пока пуст. Открой набор слов и добавь нужные карточки.",
                reply_markup=get_empty_dictionary_keyboard(),
            )
            await callback.answer()
            return

        first_card = saved_cards[0]
        await callback.message.edit_text(
            format_dictionary_card_text(first_card, 1, len(saved_cards)),
            reply_markup=get_dictionary_keyboard(1, len(saved_cards)),
        )
        await callback.answer()
        return

    if section_key == "progress":
        with session_manager() as session:
            stats = get_progress_stats(session, callback.from_user.id)

        await callback.message.edit_text(
            format_progress_text(stats),
            reply_markup=get_back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    if section_key == "settings":
        with session_manager() as session:
            settings = get_user_settings(session, callback.from_user.id)

        if settings is None:
            await callback.answer("Не удалось открыть настройки.", show_alert=True)
            return

        await callback.message.edit_text(
            format_settings_text(settings),
            reply_markup=get_settings_keyboard(),
        )
        await callback.answer()
        return

    section_text = SECTION_TEXTS.get(section_key, "Раздел пока недоступен.")

    await callback.message.edit_text(
        section_text,
        reply_markup=get_back_to_menu_keyboard(),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "learn:sets")
async def show_word_sets(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None:
        await callback.answer()
        return

    with session_manager() as session:
        word_sets = get_word_sets(session, callback.from_user.id)

    await callback.message.edit_text(
        SECTION_TEXTS["lessons"],
        reply_markup=get_word_sets_keyboard(word_sets),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("training:mode:"))
async def choose_training_mode(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    mode = callback.data.split(":")[2]
    if mode == "challenge":
        with session_manager() as session:
            next_level, word_sets = get_challenge_word_sets(session, callback.from_user.id)

        if next_level is None:
            await callback.message.edit_text(
                "Ты уже на самом высоком уровне. Можно проходить обычные тренировки B2.",
                reply_markup=get_training_mode_keyboard(),
            )
            await callback.answer()
            return

        await callback.message.edit_text(
            f"Вызов выше уровня: темы уровня {next_level}. Если результат будет сильным, бот предложит повысить уровень.",
            reply_markup=get_training_sets_keyboard_for_mode(word_sets, mode),
        )
        await callback.answer()
        return

    with session_manager() as session:
        word_sets = get_word_sets(session, callback.from_user.id)

    mode_text = (
        "Обычный тест: бот задаст все вопросы по выбранной теме."
        if mode == "normal"
        else "Режим до первой ошибки: бот продолжает задавать вопросы, пока ответ правильный."
    )
    await callback.message.edit_text(
        mode_text,
        reply_markup=get_training_sets_keyboard_for_mode(word_sets, mode),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "dictionary:manual:add")
async def start_manual_word_add(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await state.set_state(AddWordState.waiting_for_word)
    await callback.message.edit_text(
        "Добавление своего слова\n\n"
        "Напиши слово или фразу на изучаемом языке, которую хочешь сохранить."
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("learn:open:"))
async def open_recommended_learning_card(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    _, _, set_code, position_text = callback.data.split(":")
    position = int(position_text)

    with session_manager() as session:
        card_data = get_card_by_position(session, set_code, position, callback.from_user.id)

    if card_data is None:
        await callback.answer("Не удалось открыть карточку.", show_alert=True)
        return

    word_set, card = card_data
    total = len(word_set.cards)
    await callback.message.edit_text(
        format_learning_card_text(
            word_set.title,
            card.foreign_word,
            card.translation,
            card.example,
            position,
            total,
        ),
        reply_markup=get_card_keyboard(set_code, position, total, card.id),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("learn:set:"))
async def show_learning_card(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    _, _, set_code, position_text = callback.data.split(":")
    position = int(position_text)

    with session_manager() as session:
        card_data = get_card_by_position(session, set_code, position, callback.from_user.id)

    if card_data is None:
        await callback.answer("Не удалось открыть карточку.", show_alert=True)
        return

    word_set, card = card_data
    total = len(word_set.cards)
    await callback.message.edit_text(
        format_learning_card_text(
            word_set.title,
            card.foreign_word,
            card.translation,
            card.example,
            position,
            total,
        ),
        reply_markup=get_card_keyboard(set_code, position, total, card.id),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("dictionary:add:"))
async def save_card_to_dictionary(callback: CallbackQuery, session_manager) -> None:
    if callback.data is None:
        await callback.answer()
        return

    card_id = int(callback.data.split(":")[2])
    with session_manager() as session:
        added = save_word_for_user(session, callback.from_user.id, card_id)

    if added:
        await callback.answer("Слово добавлено в словарь.")
    else:
        await callback.answer("Это слово уже есть в словаре.")


@callbacks_router.callback_query(F.data.startswith("dictionary:view:"))
async def show_dictionary_card(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    position = int(callback.data.split(":")[2])
    with session_manager() as session:
        saved_cards = get_user_saved_cards(session, callback.from_user.id)
        card = get_dictionary_card_by_position(session, callback.from_user.id, position)

    if not saved_cards:
        await callback.message.edit_text(
            "Словарь пока пуст. Открой набор слов и добавь нужные карточки.",
            reply_markup=get_empty_dictionary_keyboard(),
        )
        await callback.answer()
        return

    if card is None:
        await callback.answer("Карточка не найдена.", show_alert=True)
        return

    await callback.message.edit_text(
        format_dictionary_card_text(card, position, len(saved_cards)),
        reply_markup=get_dictionary_keyboard(position, len(saved_cards)),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("dictionary:delete:"))
async def delete_dictionary_word(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    position = int(callback.data.split(":")[2])
    with session_manager() as session:
        card = get_dictionary_card_by_position(session, callback.from_user.id, position)
        deleted = False
        if card is not None:
            deleted = remove_word_for_user(session, callback.from_user.id, card.id)
        saved_cards = get_user_saved_cards(session, callback.from_user.id)

    if not deleted:
        await callback.answer("Не удалось удалить слово.", show_alert=True)
        return

    if not saved_cards:
        await callback.message.edit_text(
            "Словарь теперь пуст. Можно добавить свое слово или сохранить карточку из темы.",
            reply_markup=get_empty_dictionary_keyboard(),
        )
        await callback.answer("Слово удалено.")
        return

    next_position = min(position, len(saved_cards))
    next_card = saved_cards[next_position - 1]
    await callback.message.edit_text(
        format_dictionary_card_text(next_card, next_position, len(saved_cards)),
        reply_markup=get_dictionary_keyboard(next_position, len(saved_cards)),
    )
    await callback.answer("Слово удалено.")


@callbacks_router.callback_query(F.data.startswith("quiz:start:"))
async def start_quiz(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) == 3:
        mode = "normal"
        set_code = parts[2]
    else:
        mode = parts[2]
        set_code = parts[3]

    with session_manager() as session:
        question = build_quiz_question(session, set_code, 1, callback.from_user.id)

    if question is None:
        await callback.answer("Не удалось запустить тест.", show_alert=True)
        return

    await callback.message.edit_text(
        format_quiz_question_text(question),
        reply_markup=get_quiz_keyboard(
            question.set_code,
            question.position,
            0,
            question.word_card_id,
            question.options,
            mode,
        ),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "quiz:weak:start")
async def start_weak_quiz(callback: CallbackQuery, session_manager, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return

    with session_manager() as session:
        weak_cards = get_weak_word_cards(session, callback.from_user.id)
        weak_word_ids = [card.id for card in weak_cards]
        question = build_weak_quiz_question(session, callback.from_user.id, 1, weak_word_ids)

    if question is None:
        await callback.message.edit_text(
            "Пока нет слабых слов для повторения. Пройди несколько обычных тестов, и бот соберет ошибки.",
            reply_markup=get_training_mode_keyboard(),
        )
        await callback.answer()
        return

    await state.update_data(weak_word_ids=weak_word_ids)
    await callback.message.edit_text(
        format_quiz_question_text(question),
        reply_markup=get_weak_quiz_keyboard(
            question.position,
            0,
            question.word_card_id,
            question.options,
        ),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "quiz:survival:start")
async def start_survival_quiz(callback: CallbackQuery, session_manager, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return

    with session_manager() as session:
        survival_cards = get_survival_word_cards(session, callback.from_user.id)
        survival_word_ids = [card.id for card in survival_cards]
        question = build_survival_quiz_question(
            session,
            callback.from_user.id,
            1,
            survival_word_ids,
        )
        settings = get_user_settings(session, callback.from_user.id)

    if question is None or settings is None:
        await callback.message.edit_text(
            "Не удалось запустить режим до первой ошибки.",
            reply_markup=get_training_mode_keyboard(),
        )
        await callback.answer()
        return

    await state.update_data(
        survival_word_ids=survival_word_ids,
        survival_user_level=settings.level,
    )
    await callback.message.edit_text(
        (
            "Режим до первой ошибки\n\n"
            f"Уровень: {settings.level}\n"
            f"Слов в попытке: {question.total}\n\n"
            "Бот будет задавать случайные слова из разных доступных тем. "
            "Одна ошибка завершает тренировку."
            f"\n\n{format_quiz_question_text(question)}"
        ),
        reply_markup=get_survival_quiz_keyboard(
            question.position,
            0,
            question.word_card_id,
            question.options,
        ),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "quiz:dictionary:start")
async def start_dictionary_quiz(callback: CallbackQuery, session_manager, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return

    with session_manager() as session:
        saved_cards = get_user_saved_cards(session, callback.from_user.id)
        dictionary_word_ids = [card.id for card in saved_cards]
        random.shuffle(dictionary_word_ids)
        dictionary_word_ids = dictionary_word_ids[:10]
        question = build_dictionary_quiz_question(
            session,
            callback.from_user.id,
            1,
            dictionary_word_ids,
        )

    if question is None:
        await callback.message.edit_text(
            "В словаре пока нет слов для теста. Добавь слова из карточек или вручную.",
            reply_markup=get_empty_dictionary_keyboard(),
        )
        await callback.answer()
        return

    await state.update_data(dictionary_word_ids=dictionary_word_ids)
    await callback.message.edit_text(
        format_quiz_question_text(question),
        reply_markup=get_dictionary_quiz_keyboard(
            question.position,
            0,
            question.word_card_id,
            question.options,
        ),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("quiz:dictionary:answer:"))
async def process_dictionary_quiz_answer(callback: CallbackQuery, session_manager, state: FSMContext) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    _, _, _, position_text, score_text, correct_card_id_text, option_index_text = callback.data.split(":")
    position = int(position_text)
    score = int(score_text)
    correct_card_id = int(correct_card_id_text)
    option_index = int(option_index_text)
    data = await state.get_data()
    dictionary_word_ids = data.get("dictionary_word_ids")
    if not isinstance(dictionary_word_ids, list) or not dictionary_word_ids:
        await callback.answer("Тест устарел. Запусти тест по словарю заново.", show_alert=True)
        return

    with session_manager() as session:
        question = build_dictionary_quiz_question(
            session,
            callback.from_user.id,
            position,
            dictionary_word_ids,
        )

    if question is None or question.word_card_id != correct_card_id:
        await callback.answer("Тест устарел. Запусти тест по словарю заново.", show_alert=True)
        return

    is_correct = 0 <= option_index < len(question.options) and question.options[option_index] == question.correct_translation
    new_score = score + 1 if is_correct else score

    with session_manager() as session:
        record_word_answer_progress(session, callback.from_user.id, question.word_card_id, is_correct)

    if position < question.total:
        with session_manager() as session:
            next_question = build_dictionary_quiz_question(
                session,
                callback.from_user.id,
                position + 1,
                dictionary_word_ids,
            )

        if next_question is None:
            await callback.answer("Не удалось открыть следующий вопрос.", show_alert=True)
            return

        feedback = "Верно!" if is_correct else f"Неверно. Правильный ответ: {question.correct_translation}"
        await callback.message.edit_text(
            f"{feedback}\n\n{format_quiz_question_text(next_question)}",
            reply_markup=get_dictionary_quiz_keyboard(
                next_question.position,
                new_score,
                next_question.word_card_id,
                next_question.options,
            ),
        )
        await callback.answer()
        return

    feedback = "Верно!" if is_correct else f"Неверно. Правильный ответ: {question.correct_translation}"
    with session_manager() as session:
        record_quiz_attempt(session, callback.from_user.id, "dictionary", question.total, new_score)

    await callback.message.edit_text(
        f"{feedback}\n\n{format_quiz_result_text('Мой словарь', new_score, question.total)}",
        reply_markup=get_quiz_result_keyboard("dictionary"),
    )
    await state.update_data(dictionary_word_ids=[])
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("quiz:survival:answer:"))
async def process_survival_quiz_answer(callback: CallbackQuery, session_manager, state: FSMContext) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    _, _, _, position_text, score_text, correct_card_id_text, option_index_text = callback.data.split(":")
    position = int(position_text)
    score = int(score_text)
    correct_card_id = int(correct_card_id_text)
    option_index = int(option_index_text)
    data = await state.get_data()
    survival_word_ids = data.get("survival_word_ids")
    user_level = data.get("survival_user_level")
    if not isinstance(survival_word_ids, list) or not survival_word_ids:
        await callback.answer("Тест устарел. Запусти режим заново.", show_alert=True)
        return

    with session_manager() as session:
        question = build_survival_quiz_question(
            session,
            callback.from_user.id,
            position,
            survival_word_ids,
        )

    if question is None or question.word_card_id != correct_card_id:
        await callback.answer("Тест устарел. Запусти режим заново.", show_alert=True)
        return

    is_correct = 0 <= option_index < len(question.options) and question.options[option_index] == question.correct_translation
    new_score = score + 1 if is_correct else score

    with session_manager() as session:
        record_word_answer_progress(session, callback.from_user.id, question.word_card_id, is_correct)

    if not is_correct:
        with session_manager() as session:
            record_quiz_attempt(session, callback.from_user.id, "survival", position, new_score)

        await callback.message.edit_text(
            format_survival_result_text(question.set_title, new_score, question.correct_translation),
            reply_markup=get_quiz_result_keyboard("survival"),
        )
        await state.update_data(survival_word_ids=[])
        await callback.answer()
        return

    if position < question.total:
        with session_manager() as session:
            next_question = build_survival_quiz_question(
                session,
                callback.from_user.id,
                position + 1,
                survival_word_ids,
            )

        if next_question is None:
            await callback.answer("Не удалось открыть следующий вопрос.", show_alert=True)
            return

        await callback.message.edit_text(
            f"Верно!\n\n{format_quiz_question_text(next_question)}",
            reply_markup=get_survival_quiz_keyboard(
                next_question.position,
                new_score,
                next_question.word_card_id,
                next_question.options,
            ),
        )
        await callback.answer()
        return

    suggested_level = get_next_level(user_level) if isinstance(user_level, str) else None
    with session_manager() as session:
        record_quiz_attempt(session, callback.from_user.id, "survival", question.total, new_score)

    await callback.message.edit_text(
        format_perfect_survival_result_text(new_score, suggested_level),
        reply_markup=get_quiz_result_keyboard("survival", suggested_level=suggested_level),
    )
    await state.update_data(survival_word_ids=[])
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("quiz:weak:answer:"))
async def process_weak_quiz_answer(callback: CallbackQuery, session_manager, state: FSMContext) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    _, _, _, position_text, score_text, correct_card_id_text, option_index_text = callback.data.split(":")
    position = int(position_text)
    score = int(score_text)
    correct_card_id = int(correct_card_id_text)
    option_index = int(option_index_text)
    data = await state.get_data()
    weak_word_ids = data.get("weak_word_ids")
    if not isinstance(weak_word_ids, list) or not weak_word_ids:
        await callback.answer("Тест устарел. Запусти повторение ошибок заново.", show_alert=True)
        return

    with session_manager() as session:
        question = build_weak_quiz_question(session, callback.from_user.id, position, weak_word_ids)

    if question is None or question.word_card_id != correct_card_id:
        await callback.answer("Тест устарел. Открой повторение ошибок заново.", show_alert=True)
        return

    is_correct = 0 <= option_index < len(question.options) and question.options[option_index] == question.correct_translation
    new_score = score + 1 if is_correct else score

    with session_manager() as session:
        record_word_answer_progress(session, callback.from_user.id, question.word_card_id, is_correct)

    if position < question.total:
        with session_manager() as session:
            next_question = build_weak_quiz_question(
                session,
                callback.from_user.id,
                position + 1,
                weak_word_ids,
            )

        if next_question is None:
            await callback.answer("Не удалось открыть следующий вопрос.", show_alert=True)
            return

        feedback = "Верно!" if is_correct else f"Неверно. Правильный ответ: {question.correct_translation}"
        await callback.message.edit_text(
            f"{feedback}\n\n{format_quiz_question_text(next_question)}",
            reply_markup=get_weak_quiz_keyboard(
                next_question.position,
                new_score,
                next_question.word_card_id,
                next_question.options,
            ),
        )
        await callback.answer()
        return

    feedback = "Верно!" if is_correct else f"Неверно. Правильный ответ: {question.correct_translation}"
    with session_manager() as session:
        record_quiz_attempt(session, callback.from_user.id, "weak", question.total, new_score)

    await callback.message.edit_text(
        f"{feedback}\n\n{format_quiz_result_text('Повторение ошибок', new_score, question.total)}",
        reply_markup=get_quiz_result_keyboard("weak"),
    )
    await state.update_data(weak_word_ids=[])
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("quiz:answer:"))
async def process_quiz_answer(callback: CallbackQuery, session_manager) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) == 7:
        _, _, set_code, position_text, score_text, correct_card_id_text, option_index_text = parts
        mode = "normal"
    else:
        _, _, mode, set_code, position_text, score_text, correct_card_id_text, option_index_text = parts
    position = int(position_text)
    score = int(score_text)
    correct_card_id = int(correct_card_id_text)
    option_index = int(option_index_text)

    with session_manager() as session:
        question = build_quiz_question(session, set_code, position, callback.from_user.id)

    if question is None or question.word_card_id != correct_card_id:
        await callback.answer("Тест устарел. Запусти его заново.", show_alert=True)
        return

    is_correct = 0 <= option_index < len(question.options) and question.options[option_index] == question.correct_translation
    new_score = score + 1 if is_correct else score

    with session_manager() as session:
        record_word_answer_progress(session, callback.from_user.id, question.word_card_id, is_correct)

    if mode == "survival" and not is_correct:
        with session_manager() as session:
            record_quiz_attempt(session, callback.from_user.id, set_code, position, new_score)

        await callback.message.edit_text(
            format_survival_result_text(question.set_title, new_score, question.correct_translation),
            reply_markup=get_quiz_result_keyboard(set_code, mode),
        )
        await callback.answer()
        return

    if position < question.total:
        with session_manager() as session:
            next_question = build_quiz_question(
                session,
                set_code,
                position + 1,
                callback.from_user.id,
            )

        if next_question is None:
            await callback.answer("Не удалось открыть следующий вопрос.", show_alert=True)
            return

        feedback = "Верно!" if is_correct else f"Неверно. Правильный ответ: {question.correct_translation}"
        await callback.message.edit_text(
            f"{feedback}\n\n{format_quiz_question_text(next_question)}",
            reply_markup=get_quiz_keyboard(
                next_question.set_code,
                next_question.position,
                new_score,
                next_question.word_card_id,
                next_question.options,
                mode,
            ),
        )
        await callback.answer()
        return

    with session_manager() as session:
        record_quiz_attempt(session, callback.from_user.id, set_code, question.total, new_score)
        set_level = get_word_set_level(session, set_code)
        settings = get_user_settings(session, callback.from_user.id)

    suggested_level = get_suggested_level(mode, new_score, question.total, set_level, settings.level if settings else None)

    feedback = "Верно!" if is_correct else f"Неверно. Правильный ответ: {question.correct_translation}"
    await callback.message.edit_text(
        f"{feedback}\n\n{format_quiz_result_text(question.set_title, new_score, question.total, mode, set_level, suggested_level)}",
        reply_markup=get_quiz_result_keyboard(set_code, mode, suggested_level),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "settings:open:level")
async def show_level_settings(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        "Выбери текущий уровень подготовки.",
        reply_markup=get_level_keyboard(),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "settings:open:language")
async def show_language_settings(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        "Выбери язык для обучения. Прогресс по другим языкам сохранится.",
        reply_markup=get_language_keyboard(),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data == "settings:open:reminders")
async def show_reminder_settings(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        "Настрой напоминания о занятиях.",
        reply_markup=get_reminder_keyboard(),
    )
    await callback.answer()


@callbacks_router.callback_query(F.data.startswith("settings:set:level:"))
async def set_level(callback: CallbackQuery, session_manager) -> None:
    if callback.data is None:
        await callback.answer()
        return

    level = callback.data.split(":")[3]
    with session_manager() as session:
        updated = update_user_level(session, callback.from_user.id, level)
        settings = get_user_settings(session, callback.from_user.id)

    if not updated or settings is None or callback.message is None:
        await callback.answer("Не удалось обновить уровень.", show_alert=True)
        return

    await callback.message.edit_text(
        format_settings_text(settings),
        reply_markup=get_settings_keyboard(),
    )
    await callback.answer("Уровень обновлен.")


@callbacks_router.callback_query(F.data.startswith("settings:set:language:"))
async def set_language(callback: CallbackQuery, session_manager) -> None:
    if callback.data is None:
        await callback.answer()
        return

    language = callback.data.split(":")[3]
    with session_manager() as session:
        updated = update_user_language(session, callback.from_user.id, language)
        settings = get_user_settings(session, callback.from_user.id)

    if not updated or settings is None or callback.message is None:
        await callback.answer("Не удалось обновить язык.", show_alert=True)
        return

    await callback.message.edit_text(
        format_settings_text(settings),
        reply_markup=get_settings_keyboard(),
    )
    await callback.answer("Язык обновлен.")


@callbacks_router.callback_query(F.data.startswith("settings:set:reminders:"))
async def set_reminders(callback: CallbackQuery, session_manager) -> None:
    if callback.data is None:
        await callback.answer()
        return

    reminder_value = callback.data.split(":", maxsplit=3)[3]
    enabled = reminder_value != "off"
    reminder_time = reminder_value if enabled else None

    with session_manager() as session:
        updated = update_user_reminders(
            session,
            callback.from_user.id,
            enabled,
            reminder_time,
        )
        settings = get_user_settings(session, callback.from_user.id)

    if not updated or settings is None or callback.message is None:
        await callback.answer("Не удалось обновить напоминания.", show_alert=True)
        return

    await callback.message.edit_text(
        format_settings_text(settings),
        reply_markup=get_settings_keyboard(),
    )
    await callback.answer("Настройки напоминаний обновлены.")


def format_learning_card_text(
    set_title: str,
    foreign_word: str,
    translation: str,
    example: str,
    position: int,
    total: int,
) -> str:
    return (
        f"Набор: {set_title}\n"
        f"Карточка {position}/{total}\n\n"
        f"Слово: {foreign_word}\n"
        f"Перевод: {translation}\n\n"
        f"Пример: {example}"
    )


def format_dictionary_card_text(card, position: int, total: int) -> str:
    return (
        f"Мой словарь\n"
        f"Слово {position}/{total}\n\n"
        f"Слово: {card.foreign_word}\n"
        f"Перевод: {card.translation}\n\n"
        f"Пример: {card.example}"
    )


def format_quiz_question_text(question) -> str:
    options_text = "\n".join(
        f"{index + 1}. {option}" for index, option in enumerate(question.options)
    )
    return (
        f"Тест по набору: {question.set_title}\n"
        f"Вопрос {question.position}/{question.total}\n\n"
        f"Как переводится слово: {question.foreign_word}?\n\n"
        f"{options_text}"
    )


def format_quiz_result_text(
    set_title: str,
    score: int,
    total: int,
    mode: str = "normal",
    set_level: str | None = None,
    suggested_level: str | None = None,
) -> str:
    percent = round((score / total) * 100) if total else 0
    title = "Тест завершен"
    if mode == "challenge":
        title = "Вызов выше уровня завершен"
    elif mode == "survival":
        title = "Тренировка до первой ошибки завершена"

    level_text = f"\nУровень темы: {set_level}" if set_level else ""
    suggestion_text = (
        f"\n\nТы ответил на {score} вопросов уровня {set_level}, который выше текущего. "
        f"Можно переходить на уровень {suggested_level}."
        if suggested_level is not None and set_level is not None
        else ""
    )
    return (
        f"{title}\n"
        f"Набор: {set_title}{level_text}\n\n"
        f"Правильных ответов: {score} из {total}\n"
        f"Результат: {percent}%"
        f"{suggestion_text}"
    )


def format_survival_result_text(set_title: str, score: int, correct_translation: str) -> str:
    return (
        "Тренировка до первой ошибки завершена\n"
        f"Набор: {set_title}\n\n"
        f"Серия правильных ответов: {score}\n"
        f"Правильный ответ на последний вопрос: {correct_translation}\n\n"
        "Можно попробовать еще раз или открыть прогресс."
    )


def format_perfect_survival_result_text(score: int, suggested_level: str | None) -> str:
    level_text = (
        f"\n\nТы прошел все слова без ошибок. Можно переходить на уровень {suggested_level}."
        if suggested_level is not None
        else "\n\nТы прошел все доступные слова без ошибок. Это максимальный уровень."
    )
    return (
        "Идеальная тренировка\n\n"
        f"Правильных ответов подряд: {score}\n"
        f"{level_text}"
    )


def get_suggested_level(
    mode: str,
    score: int,
    total: int,
    set_level: str | None,
    user_level: str | None,
) -> str | None:
    if mode != "challenge" or set_level is None or user_level is None:
        return None
    if get_next_level(user_level) != set_level:
        return None
    if total == 0 or score / total < 0.8:
        return None
    return set_level


def format_progress_text(stats) -> str:
    goal_text = (
        "выполнена ✅"
        if stats.today_attempts >= 1
        else "осталось пройти 1 тренировку"
    )
    strongest_text = stats.strongest_set_title or "пока нет данных"
    weakest_text = stats.weakest_set_title or "пока нет данных"
    return (
        "📊 Мой прогресс\n\n"
        "🎯 Цель дня\n"
        f"Тренировок сегодня: {stats.today_attempts}\n"
        f"Статус: {goal_text}\n\n"
        "🧠 Обучение\n"
        f"Сохранено слов: {stats.saved_words_count}\n"
        f"Пройдено тестов: {stats.total_attempts}\n"
        f"Всего вопросов: {stats.total_questions}\n"
        f"Правильных ответов: {stats.total_correct}\n\n"
        "📈 Результаты\n"
        f"Средняя точность: {stats.accuracy_percent}%\n"
        f"Лучший результат: {stats.best_result} правильных ответов\n\n"
        "🔁 Повторение\n"
        f"Слабых слов: {stats.weak_words_count}\n"
        f"Сильная тема: {strongest_text}\n"
        f"Тема для повторения: {weakest_text}"
    )


def format_settings_text(settings) -> str:
    language_name = format_language_name(settings.current_language)
    reminder_status = (
        f"включены, время: {settings.reminder_time}"
        if settings.reminders_enabled and settings.reminder_time
        else "выключены"
    )
    return (
        "Настройки профиля\n\n"
        f"Язык: {language_name}\n"
        f"Уровень: {settings.level}\n"
        f"Напоминания: {reminder_status}\n\n"
        "Выбери параметр, который хочешь изменить.\n"
        "Язык и уровень влияют на доступные наборы слов в разделе обучения."
    )


def format_language_name(language: str) -> str:
    return {
        "English": "Английский",
        "Spanish": "Испанский",
        "Italian": "Итальянский",
    }.get(language, language)


@callbacks_router.callback_query(F.data)
async def handle_unknown_callback(callback: CallbackQuery) -> None:
    if callback.message is not None:
        await callback.message.edit_text(
            "Эта кнопка устарела или больше недоступна. Открой главное меню и выбери действие заново.",
            reply_markup=get_main_menu_keyboard(),
        )
    await callback.answer("Кнопка устарела.")
