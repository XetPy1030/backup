from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config
import asyncio
from aiogram import filters, types


@dp.message_handler(commands="profile")
async def cmd_test1(message: types.Message):
    id = message.chat.id
    user = db.get_user(id)
    from_us = f'<a href="tg://user?id={user["from"]}">{user["from"]}</a>' if user["from"] else "нет"
    await message.answer(f'id: {id}\nПриглашён: {from_us}\nПриглашённых: {len(user["new_users"])}\nСсылка для приглашения: https://t.me/Mango_agency_bot?start=ref-{id}') 


@dp.message_handler(commands="other_profile")
async def cmd_test1(message: types.Message):
    db.set_status(message.chat.id, "profile")
    await message.answer("Отправьте id или перешлите сообщение от пользователя")

