import db
import config
import lang
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
    )


def run(bot=None, admin_id=None, account=None, message=None, markups=None):
    if message.text in commands.keys():
        commands[message.text](
            bot=bot,
            admin_id=admin_id,
            account=account,
            message=message,
            markups=markups
            )
        return


class commands:
    @staticmethod
    def shop(bot=None, admin_id=None, account=None, message=None,
             markups=None):
        products = db.get_products_work()
        buttons = []

        for product in products:
            buttons.append([
                InlineKeyboardButton(
                    product['name'],
                    callback_data=f"product:{product['product_id']}")
                ])

        buttons.append([
            InlineKeyboardButton(
                "📆 Календарь мероприятий",
                callback_data="calendar:info")
            ])

        keyboard = None
        if len(buttons) > 0:
            keyboard = InlineKeyboardMarkup(buttons)

        message.reply('Доступные подписки:', reply_markup=keyboard)

    @staticmethod
    def my_subscribe(bot=None, admin_id=None, account=None, message=None,
                     markups=None):
        subs = db.get_subscriber(message.chat.id)
        buttons = []

        for sub in subs:
            if sub['type'] == config.subscribers_type['product']: 
                if db.get_sub(sub['sub_id']) != None:
                    buttons.append([InlineKeyboardButton(db.get_product(db.get_sub(sub['sub_id'])['product_id'])['name'], callback_data=f"subscriber:{sub['sub_id']}")])

            if sub['type'] == config.subscribers_type['calendar']: buttons.append([InlineKeyboardButton('📆 Календарь мероприятий', callback_data=f"subscriber:calendar")])

        keyboard = None
        if len(buttons) > 0: keyboard = InlineKeyboardMarkup(buttons)

        message.reply('Список ваших активных подписок:', reply_markup=keyboard)

    @staticmethod  # ready
    def feedback(bot=None, admin_id=None, account=None, message=None,
                  markups=None):
        message.reply(lang.feedback_text, reply_markup=markups['back'])
        db.set_status(message.chat.id, 'feedback')

    @staticmethod  # ready
    def reviews(bot=None, admin_id=None, account=None, message=None,
                  markups=None):
        message.reply('https://t.me/donclub_feedback')

    @staticmethod
    def profile(bot=None, admin_id=None, account=None, message=None,
                markups=None):
        count = db.get_count_refs(message.chat.id)[0]['COUNT(*)']

        message.reply(
            lang.referral_program.format(
                balance=round(db.get_balance(message.chat.id), 2),
                count=count,
                username=bot.get_me().username,
                chat_id=message.chat.id,
                ref_procent=config.ref_procent),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    '💸 Заказать вывод',
                    callback_data='output'
                    )
                ]])
        )

    @staticmethod
    def start(bot=None, admin_id=None, account=None, message=None,
              markups=None):
        if db.get_user(message.chat.id) is None:
            try:
                link = message.text.split(' ')[1].split('-')[0]
                data = int(message.text.split(' ')[1].split('-')[1])
            except: 
                link = None

            if link is not None:
                if link == 'ref':
                    db.add_new_referal(data, message.chat.id)

            db.add_user(message.chat.id)

        else:
            if db.get_user(message.chat.id)['del'] == 1:
                db.set_delete(message.chat.id, 0)

        message.reply(f'Привет, {message.from_user.first_name}! Здесь ты можешь купить подписку в Don | Invest Club!', reply_markup=markups["menu"])


commands = {
    "🛍 Магазин": commands.shop,
    "👤 Мои подписки": commands.my_subscribe,
    "💬 Отзывы участников клуба": commands.reviews,
    "📢 Реф. Программа": commands.profile,
    "Обратная связь": commands.feedback,
    "/start": commands.start,
}
