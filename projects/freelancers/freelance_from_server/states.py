from aiogram.dispatcher.filters.state import StatesGroup, State


class AddStates(StatesGroup):
    type = State()
    chat = State()
