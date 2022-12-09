from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice, reversed_buttons
import asyncio
from aiogram import filters, types


@dp.message_handler(db_status=[db, 'feedback'], content_types=types.message.ContentTypes.all())
async def write_feedback(message: types.Message):
    await bot.forward_message(
        chat_id=int(config['Links']['send_feedback']),
        from_chat_id=message.chat.id,
        message_id=message.message_id
        )
    await message.reply(lang['sended_msg'])
