import logging
from aiogram import Bot, Dispatcher, executor, types

from utils import states, my_filters, db
from core import bot, dp

logging.basicConfig(level=logging.INFO)


dp.filters_factory.bind(my_filters.StatusCheck, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(my_filters.IdCheck, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(my_filters.AdminCheck, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(my_filters.InlineFilter, event_handlers=[dp.callback_query_handlers])


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "🏠 Главное меню"),
        # types.BotCommand("start", "♻️Перезапуск бота"),
        # types.BotCommand("profile", "Реферальная программа"),
        # types.BotCommand("other_profile", "Другой профиль"),
    ])


import commands

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
