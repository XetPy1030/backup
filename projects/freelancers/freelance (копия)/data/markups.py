from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from . import lang

inline_rent_choice = InlineKeyboardMarkup()
inline_rent_choice.add(
    InlineKeyboardButton(lang.rent_1, callback_data="rent_give"),
    InlineKeyboardButton(lang.rent_2, callback_data="rent_get")
)

button_rent_is_long_time = ReplyKeyboardMarkup()
button_rent_is_long_time.add(
    *[KeyboardButton(i) for i in lang.rents_time]
)

button_null = ReplyKeyboardRemove()
