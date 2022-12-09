from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


class StatusCheck(BoundFilter):
    key = 'db_status'

    def __init__(self, db_status: list):
        self.db, self.status = db_status

    async def check(self, message: types.Message) -> bool:
        return self.db.get_status(message.chat.id).split(':')[0] == self.status


class AdminCheck(BoundFilter):
    key = 'db_admin'

    def __init__(self, db_admin: list):
        self.db, self.admin = db_admin

    async def check(self, message: types.Message) -> bool:
        return self.db.is_admin(message.chat.id)


class IdCheck(BoundFilter):
    key = 'checks'

    def __init__(self, checks):
        self.db, self.bot = checks

    async def check(self, message: types.Message) -> bool:
        # print(message.text)
        if message.reply_to_message and message.reply_to_message.from_user.id == self.bot.id and message.reply_to_message.forward_from:
            try:
                # await message.forward(message.reply_to_message.forward_from.id)
                await message.answer('Успешно')
            except Exception as ex:
                await message.answer(f'Ошибка: {ex}')
            
            return True

        # self.db.get_user(message.chat.id)
        self.db.update_user(message.chat.id)
        return False


class InlineFilter(BoundFilter):
    key = 'status_inline'

    def __init__(self, status_inline):
        self.query = status_inline

    async def check(self, inline_query: types.CallbackQuery) -> bool:
        return inline_query.data.split(':')[0] == self.query
