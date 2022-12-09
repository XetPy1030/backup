from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

bot = Bot(token=config['Login']['token'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
bot.parse_mode = "HTML"

__all__ = ["bot", "dp"]
