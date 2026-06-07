from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.services.learning import WordSetView


def get_word_sets_keyboard(word_sets: list[WordSetView]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"{word_set.title} ({word_set.level}) — {word_set.recommendation_reason}",
                callback_data=f"learn:open:{word_set.code}:{word_set.recommended_position}",
            )
        ]
        for word_set in word_sets
    ]
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_training_sets_keyboard(word_sets: list[WordSetView]) -> InlineKeyboardMarkup:
    return get_training_sets_keyboard_for_mode(word_sets, "normal")


def get_training_mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Обычный тест", callback_data="training:mode:normal")],
            [InlineKeyboardButton(text="До первой ошибки", callback_data="quiz:survival:start")],
            [InlineKeyboardButton(text="Повторить ошибки", callback_data="quiz:weak:start")],
            [InlineKeyboardButton(text="Вызов выше уровня", callback_data="training:mode:challenge")],
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")],
        ]
    )


def get_training_sets_keyboard_for_mode(
    word_sets: list[WordSetView],
    mode: str,
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"{word_set.title} ({word_set.level})",
                callback_data=f"quiz:start:{mode}:{word_set.code}",
            )
        ]
        for word_set in word_sets
    ]
    rows.append([InlineKeyboardButton(text="Назад к режимам", callback_data="section:training")])
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_card_keyboard(set_code: str, position: int, total: int, card_id: int) -> InlineKeyboardMarkup:
    navigation_row = []
    if position > 1:
        navigation_row.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущее",
                callback_data=f"learn:set:{set_code}:{position - 1}",
            )
        )
    if position < total:
        navigation_row.append(
            InlineKeyboardButton(
                text="Следующее ➡️",
                callback_data=f"learn:set:{set_code}:{position + 1}",
            )
        )

    keyboard = []
    if navigation_row:
        keyboard.append(navigation_row)
    keyboard.append(
        [InlineKeyboardButton(text="Добавить в словарь", callback_data=f"dictionary:add:{card_id}")]
    )
    keyboard.append([InlineKeyboardButton(text="Пройти тест по набору", callback_data=f"quiz:start:normal:{set_code}")])
    keyboard.append([InlineKeyboardButton(text="К наборам слов", callback_data="learn:sets")])
    keyboard.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_dictionary_keyboard(position: int, total: int) -> InlineKeyboardMarkup:
    navigation_row = []
    if position > 1:
        navigation_row.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущее",
                callback_data=f"dictionary:view:{position - 1}",
            )
        )
    if position < total:
        navigation_row.append(
            InlineKeyboardButton(
                text="Следующее ➡️",
                callback_data=f"dictionary:view:{position + 1}",
            )
        )

    keyboard = []
    if navigation_row:
        keyboard.append(navigation_row)
    keyboard.append([InlineKeyboardButton(text="Добавить свое слово", callback_data="dictionary:manual:add")])
    keyboard.append([InlineKeyboardButton(text="Тест по словарю", callback_data="quiz:dictionary:start")])
    keyboard.append([InlineKeyboardButton(text="Удалить это слово", callback_data=f"dictionary:delete:{position}")])
    keyboard.append([InlineKeyboardButton(text="К наборам слов", callback_data="learn:sets")])
    keyboard.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_empty_dictionary_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить свое слово", callback_data="dictionary:manual:add")],
            [InlineKeyboardButton(text="К наборам слов", callback_data="learn:sets")],
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")],
        ]
    )


def get_quiz_keyboard(
    set_code: str,
    position: int,
    score: int,
    correct_card_id: int,
    option_values: list[str],
    mode: str = "normal",
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz:answer:{mode}:{set_code}:{position}:{score}:{correct_card_id}:{index}",
            )
        ]
        for index, option in enumerate(option_values)
    ]
    rows.append([InlineKeyboardButton(text="Назад к тренировке", callback_data="section:training")])
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_weak_quiz_keyboard(
    position: int,
    score: int,
    correct_card_id: int,
    option_values: list[str],
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz:weak:answer:{position}:{score}:{correct_card_id}:{index}",
            )
        ]
        for index, option in enumerate(option_values)
    ]
    rows.append([InlineKeyboardButton(text="Назад к тренировке", callback_data="section:training")])
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_survival_quiz_keyboard(
    position: int,
    score: int,
    correct_card_id: int,
    option_values: list[str],
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz:survival:answer:{position}:{score}:{correct_card_id}:{index}",
            )
        ]
        for index, option in enumerate(option_values)
    ]
    rows.append([InlineKeyboardButton(text="Назад к тренировке", callback_data="section:training")])
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_dictionary_quiz_keyboard(
    position: int,
    score: int,
    correct_card_id: int,
    option_values: list[str],
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz:dictionary:answer:{position}:{score}:{correct_card_id}:{index}",
            )
        ]
        for index, option in enumerate(option_values)
    ]
    rows.append([InlineKeyboardButton(text="Назад к словарю", callback_data="section:dictionary")])
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_quiz_result_keyboard(
    set_code: str,
    mode: str = "normal",
    suggested_level: str | None = None,
) -> InlineKeyboardMarkup:
    if set_code == "weak":
        retry_callback = "quiz:weak:start"
    elif set_code == "survival":
        retry_callback = "quiz:survival:start"
    elif set_code == "dictionary":
        retry_callback = "quiz:dictionary:start"
    else:
        retry_callback = f"quiz:start:{mode}:{set_code}"
    rows = [
        [InlineKeyboardButton(text="Пройти тест еще раз", callback_data=retry_callback)],
        [InlineKeyboardButton(text="Открыть прогресс", callback_data="section:progress")],
    ]
    if suggested_level is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"Да, перейти на уровень {suggested_level}",
                    callback_data=f"settings:set:level:{suggested_level}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="Назад в меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )
