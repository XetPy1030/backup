from aiogram.dispatcher.filters.state import StatesGroup, State


class AddNote(StatesGroup):
    date = State()
    time = State()
    note = State()


class DeleteNote(StatesGroup):
    date = State()
    num = State()


class EditNote(StatesGroup):
    date = State()
    num = State()
    time = State()
    note = State()
