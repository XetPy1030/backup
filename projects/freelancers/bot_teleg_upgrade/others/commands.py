import db
import config
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
    )
import others.lang as lang
from others import markups


async def run(message=None, bot=None, dp=None):
    if message.text in commands_button.keys():
        await commands_button[message.text](message=message, bot=bot, dp=dp)

    if message.chat.id not in config.admin_ids:
        return


class CommandsButton:
    @staticmethod
    async def test(message=None, bot=None, dp=None):
        await message.reply(f'К фигам {message.chat.id}')

    @staticmethod
    async def shop(message=None, bot=None, dp=None):
        buttons = [[InlineKeyboardButton(product['name'], callback_data=f"product:{product['product_id']}")] for product in db.get_products_work()]
        buttons.append([InlineKeyboardButton("📆 Календарь мероприятий", callback_data="calendar:info")])

        await message.reply('Доступные подписки:', reply_markup=InlineKeyboardMarkup(buttons))

    @staticmethod
    async def my_subscription(message=None, bot=None, dp=None):
        subs = db.get_subscriber(message.chat.id)
        buttons = []

        for sub in subs:
            if sub['type'] == config.subscribers_type['product']:
                if db.get_sub(sub['sub_id']) != None:
                    buttons.append([InlineKeyboardButton(db.get_product(db.get_sub(sub['sub_id'])['product_id'])['name'], callback_data=f"subscriber:{sub['sub_id']}")])
            elif sub['type'] == config.subscribers_type['calendar']:
                buttons.append([InlineKeyboardButton('📆 Календарь мероприятий', callback_data=f"subscriber:calendar")])

        keyboard = InlineKeyboardMarkup(buttons) if len(buttons) else None
        await message.reply('Список ваших активных подписок:', reply_markup=keyboard)

    @staticmethod
    async def feedback_from_club_members(message=None, bot=None, dp=None):
        await message.reply(config.link_feedback_from_club_members)

    @staticmethod
    async def referall_program(message=None, bot=None, dp=None):
        balance = round(db.get_balance(message.chat.id), 2)
        count = db.get_count_refs(message.chat.id)[0]['COUNT(*)']
        username = (await bot.get_me()).username

        await message.reply(
            lang.referral_program.format(balance=balance, count=count, username=username, chat_id=message.chat.id, ref_procent=config.ref_procent),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(config.buttons['order_withdrawal'],callback_data='output')]]),
            parse_mode='HTML'
        )

    @staticmethod
    async def feedback(message=None, bot=None, dp=None):
        await message.reply(lang.feedback_text, reply_markup=markups.BACK)
        db.set_status(message.chat.id, 'feedback')

    @staticmethod
    async def start(message=None, bot=None, dp=None):
        if db.get_user(message.chat.id) is None:
            try:
                link = message.text.split(' ')[1].split('-')[0]
                data = int(message.text.split(' ')[1].split('-')[1])
                if link == 'ref':
                    db.add_new_referal(data, message.chat.id)
            except:
                link = None

            db.add_user(message.chat.id)
        else:
            if db.get_user(message.chat.id)['del'] == 1:
                db.set_delete(message.chat.id, 0)

        await message.reply(lang.welcome_message.format(username=message.from_user.first_name), reply_markup=markups.MENU)


class CommandsAdminButton:
    @staticmethod
    async def admin(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def export_data(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def mailing(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def add_product(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def edit_product(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def add_promocode(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def edit_promocode(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def statistics(message=None, bot=None, dp=None):
        pass


class CommandsAdmin:
    @staticmethod
    async def editProduct(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def addNextChannel(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setProductName(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setProductAbout(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def getSubsProduct(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def addSubProduct(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def onProduct(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def offProduct(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def deleteProduct(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def editSub(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setSubName(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setSubPrice(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setSubPeriod(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def onSub(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def offSub(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def deleteSub(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def editPromocode(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setPromocodeTotalCountUses(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def setPromocodeDiscount(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def onPromocode(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def offPromocode(message=None, bot=None, dp=None):
        pass

    @staticmethod
    async def deletePromocode(message=None, bot=None, dp=None):
        pass


commands_button = {
    config.buttons['shop']: CommandsButton.shop,
    config.buttons['my_subscription']: CommandsButton.my_subscription,
    config.buttons['feedback_from_club_members']: CommandsButton.feedback_from_club_members,
    config.buttons['referall_program']: CommandsButton.referall_program,
    config.buttons['feedback']: CommandsButton.feedback,
    '/start': CommandsButton.start,
    'test': CommandsButton.test,
}

commands_admin_buttons = {
    config.buttons['admin']: CommandsAdminButton.admin,
    config.buttons['export_data']: CommandsAdminButton.export_data,
    config.buttons['mailing']: CommandsAdminButton.mailing,
    config.buttons['add_product']: CommandsAdminButton.add_product,
    config.buttons['edit_product']: CommandsAdminButton.edit_product,
    config.buttons['add_promocode']: CommandsAdminButton.add_promocode,
    config.buttons['edit_promocode']: CommandsAdminButton.edit_promocode,
    config.buttons['statistics']: CommandsAdminButton.statistics,
}

commands_admin = {
    'editProduct': CommandsAdmin.editProduct,
    'addNextChannel': CommandsAdmin.addNextChannel,
    'setProductName': CommandsAdmin.setProductName,
    'setProductAbout': CommandsAdmin.setProductAbout,
    'getSubsProduct': CommandsAdmin.getSubsProduct,
    'addSubProduct': CommandsAdmin.addSubProduct,
    'onProduct': CommandsAdmin.onProduct,
    'offProduct': CommandsAdmin.offProduct,
    'deleteProduct': CommandsAdmin.deleteProduct,
    'editSub': CommandsAdmin.editSub,
    'setSubName': CommandsAdmin.setSubName,
    'setSubPrice': CommandsAdmin.setSubPrice,
    'setSubPeriod': CommandsAdmin.setSubPeriod,
    'onSub': CommandsAdmin.onSub,
    'offSub': CommandsAdmin.offSub,
    'deleteSub': CommandsAdmin.deleteSub,
    'editPromocode': CommandsAdmin.editPromocode,
    'setPromocodeTotalCountUses': CommandsAdmin.setPromocodeTotalCountUses,
    'setPromocodeDiscount': CommandsAdmin.setPromocodeDiscount,
    'onPromocode': CommandsAdmin.onPromocode,
    'offPromocode': CommandsAdmin.offPromocode,
    'deletePromocode': CommandsAdmin.deletePromocode,
}
