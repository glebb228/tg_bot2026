from aiogram.fsm.state import State, StatesGroup


class AddWordState(StatesGroup):
    waiting_for_word = State()
    waiting_for_translation = State()
    waiting_for_example = State()
