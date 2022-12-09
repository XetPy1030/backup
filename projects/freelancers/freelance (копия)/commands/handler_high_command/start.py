from core import dp
import utils.db as db
from aiogram import types
from data import lang, markups


@dp.message_handler(commands=["start", "restart"])
async def admin_panel(message: types.Message):
    await message.answer(lang.start_message, reply_markup=markups.inline_rent_choice)
