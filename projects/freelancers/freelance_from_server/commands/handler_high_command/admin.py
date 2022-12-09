from core import *
import utils.db as db
import utils.markups as markups
from config import *
from aiogram import types

@dp.message_handler(commands="admin", db_admin=[db, True])
async def cmd_test1(message: types.Message):
    db.set_admin(int(message.text[7:]), True)
    await message.answer("Успешно")
