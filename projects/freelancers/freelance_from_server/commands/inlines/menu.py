from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice
import asyncio
from aiogram import filters, types

@dp.callback_query_handler(status_inline='menu')
async def dgcv(inline_query: types.CallbackQuery):
    message = inline_query.message
    await message.answer_animation(
        open('photos/logov2.gif.mp4', 'rb'),
        caption=lang['hello'],
        reply_markup=button_menu_choice(message.chat.id)
    ) 

