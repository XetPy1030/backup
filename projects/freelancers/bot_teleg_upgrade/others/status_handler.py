import db
import config
from others import markups, lang
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
    )


async def run(message=None, bot=None, dp=None):
    status = db.get_status(message.chat.id)
    if status is None:
        return
    status, *others_status = status.split(':')
    if status in commands.keys():
        return not await commands[status](message=message, bot=bot, dp=dp, status=others_status)


class commands:
    @staticmethod
    async def feedback(message=None, bot=None, dp=None, status=None):
        db.set_status(message.chat.id)
        if message.text == config.buttons['back']:
            message.reply(lang.cancel, reply_markup=markups.MENU)
            return

        await bot.send_message(
            config.send_feedback,
            text = lang.feedback_check.format(username=message.chat.username, id=message.chat.id, message=message.text)
        )
        await message.reply(lang.after_feedback, reply_markup=markups.MENU)

    @staticmethod
    async def admin(message=None, bot=None, dp=None, status=None):
        if message.text == config.buttons['back']:
            await message.reply(lang.menu, reply_markup=markups.MENU, parse_mode='HTML')
            db.set_status(message.chat.id)
            return
        return True

    @staticmethod
    async def get_txid(message=None, bot=None, dp=None, status=None):
        if message.text == config.buttons['back']:
            await message.reply(lang.menu, reply_markup=markups.MENU, parse_mode='HTML')
            db.set_status(message.chat.id)
            return

        sub_id, price, pc_id = status
        sub_id, price, pc_id = int(sub_id), float(price), int(pc_id)

        await message.reply('✅ <b>Квитанция отправлена оператору!</b>\n\nКак только мы проверим платёж - у Вас активируется подписка!\n<b>Ожидайте</b> ;)', reply_markup=MENU)
        db.set_status(message.chat.id)
        if pc_id != -1: db.set_pc_count_uses(pc_id, db.get_promocode(pc_id)['count_uses'] + 1)

        await bot.send_message(
            config.check_pay,
            f'''
<b>Проверьте платеж!</b>

Отправитель: <a href="tg://user?id={message.chat.id}">{message.from_user.first_name}</a> ({message.chat.id})

Сумма: {price}$
txid: <code>{message.text}</code>
            ''',
            reply_markup=InlineKeyboardMarkup(
                [ 
                    [InlineKeyboardButton('Подтвердить', callback_data=f'txid:approve:{sub_id}:{message.chat.id}:{price}')],
                    [InlineKeyboardButton('Отклонить', callback_data=f'txid:reject:{sub_id}:{message.chat.id}:{price}')]
                ]
            )
        )

    @staticmethod
    async def addProduct(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def editProduct(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def editSub(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def mailing(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def addPromocode(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def editPromocode(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def sendPromocode(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def output(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def sendEmail(message=None, bot=None, dp=None, status=None):
        pass

    @staticmethod
    async def getCalendarTxid(message=None, bot=None, dp=None, status=None):
        pass


commands = {
    "feedback": commands.feedback,
    "admin": commands.admin,
    "get_txid": commands.get_txid,
    "addProduct": commands.addProduct,
    "editProduct": commands.editProduct,
    "editSub": commands.editSub,
    "mailing": commands.mailing,
    "addPromocode": commands.addPromocode,
    "editPromocode": commands.editPromocode,
    "sendPromocode": commands.sendPromocode,
    "output": commands.output,
    "sendEmail": commands.sendEmail,
    "getCalendarTxid": commands.getCalendarTxid
}
