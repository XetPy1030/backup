import logging
import config
import db
from others import commands, markups, status_handler, lang

from aiogram import Bot, Dispatcher, executor, types

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['restart'])
async def restart(message: types.Message):
    db.set_status(message.chat.id)
    await message.reply(lang.menu, reply_markup=markups.MENU, parse_mode="HTML")


@dp.message_handler()
async def on_message(message: types.Message):
    if db.get_user(message.chat.id) is None or not await status_handler.run(message=message, bot=bot, dp=dp):
        await commands.run(message=message, bot=bot, dp=dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
