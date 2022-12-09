from aiogram import Dispatcher
from aiogram import executor

from data.config import SKIP_UPDATES
from loguru import logger
from loader import dp

# from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.logger_config import setup_logger


async def on_startup(dispatcher: Dispatcher):
    setup_logger()
    logger.info("Установка обработчиков...")
    import handlers

    # await on_startup_notify(dispatcher)
    await set_default_commands(dispatcher)
    logger.info(f"Бот успешно запущен...")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=SKIP_UPDATES)
