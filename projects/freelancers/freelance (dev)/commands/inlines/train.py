
from config import button_menu_choice, config, lang
from core import bot, dp
from aiogram import types
import utils.markups as markups
from time import sleep


@dp.callback_query_handler(status_inline='want_learn')
async def some_inline_handler(inline_query: types.CallbackQuery):
    msg = inline_query.message
    await msg.answer(lang['train3'])
    sleep(4)
    await msg.answer(lang['train4'], reply_markup=markups.train2)