from core import *
import utils.db as db
import utils.markups as markups
from config import *
from aiogram import filters, types


@dp.message_handler(commands="start")
async def cmd_test1(message):
    if not db.is_user(message.chat.id):
        if "ref-" in message.text:
            from_us = int(message.text.split("ref-")[1])
            db.new_user_from_old(message.chat.id, from_us)
        else: db.new_user(message.chat.id)
    db.set_status(message.chat.id, '')
    if False:
        await message.answer_document(open("photos/start.pdf", "rb"), reply_markup=markups.inline_new_start)
        # await message.answer("Выберите", reply_markup=markups.inline_new_start)
        return
    await message.answer_animation(
        open('photos/logov2.gif.mp4', 'rb'),
        caption=lang['hello'],
        reply_markup=button_menu_choice(message.chat.id)
    )