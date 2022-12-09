from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice
import asyncio
from aiogram import filters, types


@dp.message_handler(db_status=[db, 'sendid'], content_types=types.message.ContentTypes.all())
async def process_note(message: types.Message):
    # print(1)
    await bot.forward_message(
        chat_id=int(db.get_status(message.chat.id).split(":")[1]),
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    await message.reply("Готово")
    db.set_status(message.chat.id)
