from pyrogram import Client, filters, errors
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, messages_and_media
import config

class Account:
    def __init__(self) -> None:
        self.bot = Client(
            'sessions/account',
            api_id=config.account_api_id,
            api_hash=config.account_api_hash,
        )

        self.bot.start()

    def set_username(self, to):
        self.bot.update_username(to)

    def send_message(self, to):
        self.bot.send_message(to, 'Привет!')

    def add_member(self, chat_id, user_id):
        self.bot.add_chat_members(chat_id=chat_id, user_ids=user_id)

    def create_link(self, chat_id, member_limit=1):
        return self.bot.create_chat_invite_link(chat_id, member_limit=member_limit)

    def get_chat_invite_link_members(self, chat_id, invit_link):
        return self.bot.get_chat_invite_link_members(chat_id=chat_id, invite_link=invit_link)