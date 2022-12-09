from core import *
import utils.db as db
import utils.markups as markups
from config import *
from aiogram import filters, types
from time import sleep


@dp.message_handler(commands="start")
async def cmd_test1(message):
    print(message.text)
    if not db.is_user(message.chat.id):
        if "ref-" in message.text:
            from_us = int(message.text.split("ref-")[1])
            db.new_user_from_old(message.chat.id, from_us)
        else: db.new_user(message.chat.id)
    db.set_status(message.chat.id, '')
    
    if len(message.text.split()) == 2:
        if message.text.split()[1] == 'train':
            await message.answer_animation(
                open('new_photos/train.mp4', 'rb'),
                caption=lang['train1']
            )
            sleep(4)
            await message.answer(
                lang['train2'],
                reply_markup=markups.want_learn
            )
            return

    await message.answer_animation(
        open('photos/logov2.gif.mp4', 'rb'),
        caption=lang['hello'],
        reply_markup=button_menu_choice(message.chat.id)
    )