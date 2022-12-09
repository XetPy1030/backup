from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import get_markups, markups

MENU = ReplyKeyboardMarkup(get_markups(KeyboardButton, markups['menu']), True, False)
ADMIN = ReplyKeyboardMarkup(get_markups(KeyboardButton, markups['admin']), True, False)
BACK = ReplyKeyboardMarkup(get_markups(KeyboardButton, markups['back']), True, False)
