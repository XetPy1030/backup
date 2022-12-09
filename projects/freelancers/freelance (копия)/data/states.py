from aiogram.dispatcher.filters.state import State, StatesGroup


class RentGiveForm(StatesGroup):
    city = State()
    is_long_time = State()
    price = State()
    num_rooms = State()
    photos = State()

class RentGetForm(StatesGroup):
    city = State()
    is_long_time = State()
