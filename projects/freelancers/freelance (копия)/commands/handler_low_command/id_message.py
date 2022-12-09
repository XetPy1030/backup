from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config
import asyncio
from aiogram import filters, types


@dp.message_handler(commands="send_id")
async def cmd_test1(message: types.Message):
    id = int(message.text.split(" ")[1])
    db.set_status(message.chat.id, f"sendid:{id}")
    await message.answer("А теперь напиши что передать:")


@dp.callback_query_handler(status_inline='sendid')
async def dgcv(inline_query: types.CallbackQuery):
    id = int(inline_query.data.split(":")[1])
    message = inline_query.message
    await message.answer("Что передать?")
    db.set_status(message.chat.id, f"sendid:{id}")
