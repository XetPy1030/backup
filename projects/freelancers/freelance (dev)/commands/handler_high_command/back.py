from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice
import asyncio
from aiogram import filters, types


@dp.message_handler(filters.Text(buttons['back']))
async def do_back(message: types.Message):
    await message.answer_animation(
        open('photos/logov2.gif.mp4', 'rb'),
        caption=lang['hello'],
        reply_markup=button_menu_choice(message.chat.id)
    )
    db.set_status(message.chat.id, '')
