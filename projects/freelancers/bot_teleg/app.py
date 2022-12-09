from pyrogram import ( # ку
    Client, # что будем ща делать?
    filters # попробуем купить  \\\\ бд заблокана
    )
import api
import pyrogram
from pyrogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    
    )

from datetime import datetime
import schedule
from schedule import run_pending
from threading import Thread
import app_logger

import config
import db
import os
import lang
import time
from account import Account
import text_commands as cmds

"""
# Проверка платежей каждые 5 минут
# увековечим работу копилота... мы будем помнить тебя вечно...
def check_payments():
    for sub in db.get_subscriptions():
        if sub['status'] == 'pending':
            if db.get_timestamp(db.get_date_now()) > sub['finish_date']:
                db.set_subscription_status(sub['sub_id'], 'expired')
                continue
"""


bot = Client(
    'sessions/bot',
    api_id=config.api_id,
    api_hash=config.api_hash,
    bot_token=config.api_bot_token
)

admin_id = config.admin_id

logger = app_logger.get_logger(__name__)

acc = Account()

MENU = ReplyKeyboardMarkup(config.menu(KeyboardButton), True, False)
ADMIN = ReplyKeyboardMarkup(config.admin(KeyboardButton), True, False)
BACK = ReplyKeyboardMarkup(config.back(KeyboardButton), True, False)


# @bot.on_message(filters.private & filters.text)
@bot.on_message(filters.text)
def status_handler(cli, message):
    # print(message)
    if db.get_user(message.chat.id) is None:
        text(message)
        return

    if message.text == '/restart' or message.text == '⬅️ Назад':
        db.set_status(message.chat.id)
        message.reply('<b>Меню</b>', reply_markup=MENU)

    status = db.get_status(message.chat.id)

    if status is None:
        text(message)
        return

    elif status.startswith('editFinishDateUser'):
        spl = status.split(':')
        form = spl[1]
        if message.text == 'Назад':
            message.reply('Админ-Панель', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')
            return

        if form == 'start':
            # message.from_user message.sender_chat message.forward_from message.forward_from_chat
            # print(message.from_user, message.sender_chat, message.forward_from, message.forward_from_chat)
            id = message.forward_from.id if message.forward_from and not message.forward_from_chat else message.text
            subs = db.get_subscriber(id)
            msg_text = ''
            for o in range(len(subs)):
                i = subs[o]
                msg_user_id = i["user_id"]
                if i['type'] != 1:
                    # msg_text += f'{msg_user_id}[Календаль]\n'
                    # msg_text += f'/editFinishDate_{msg_user_id}_0\n\n'
                    continue
                msg_subsub_id = i["sub_id"]
                msg_sub = db.get_product(db.get_sub(msg_subsub_id)["product_id"])
                msg_sub_name = msg_sub["name"]
                msg_sub_id = msg_sub["product_id"]
                msg_subsub_name = db.get_sub(msg_subsub_id)["name"]
                msg_end_time = db.get_date_from_timestamp(i["finish_date"])
                msg_text += f'{msg_user_id}[{msg_sub_name} {msg_subsub_name}]: {msg_end_time}\n'
                msg_text += f'/editFinishDate_{msg_user_id}_{msg_subsub_id}\n\n'

            message.reply(msg_text if msg_text else 'У этого пользователя нет подписок', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')
        elif form == 'data':
            try:
                period = int(message.text)
            except:
                message.reply('Что-то тут не так!')
                return
            _, _, msg_user_id, msg_sub_id = spl
            finish_date = db.get_timestamp(db.get_next_date(days=period))
            db.set_sub_period_user(msg_sub_id, finish_date, msg_user_id)
            message.reply('<b>Готово!</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Изменение конечной даты подписки',
                new=f'Подписка {msg_sub_id} изменено дата на {finish_date} у tg://user?id={msg_user_id}'
            ))

    elif status == 'feedback':
        if message.text != '⬅️ Назад':
            bot.send_message(
                config.send_feedback,
                text = lang.feedback_check.format(username=message.chat.username if not message.chat.username is None else "Нет username",
                                                  id=message.chat.id,
                                                  message=message.text)
            )
            message.reply(lang.after_feedback, reply_markup=MENU)
        else:
            message.reply('Отменено!', reply_markup=MENU)
        db.set_status(message.chat.id)

    elif status == 'admin':
        if message.text == '⬅️ Назад':
            message.reply('<b>Меню</b>', reply_markup=MENU)
            db.set_status(message.chat.id)
        else: text(message); return

    elif 'get_txid:' in status:
        if message.text != '⬅️ Назад':
            sub_id = int(status.split(':')[1])
            price = float(status.split(':')[2])
            pc_id = int(status.split(':')[3])

            message.reply('✅ <b>Квитанция отправлена оператору!</b>\n\nКак только мы проверим платёж - у Вас активируется подписка!\n<b>Ожидайте</b> ;)', reply_markup=MENU)
            db.set_status(message.chat.id)
            if pc_id != -1: db.set_pc_count_uses(pc_id, db.get_promocode(pc_id)['count_uses'] + 1)

            bot.send_message(
                config.send_pay,
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

        else:
            message.reply('<b>Меню</b>', reply_markup=MENU)
            db.set_status(message.chat.id)

    elif 'addProduct:' in status:
        get = status.split(':')[1]

        if message.text != '⬅️ Назад':
            if get == 'channel_id':
                if message.forward_from_chat != None:
                    product_id = db.add_product(message.forward_from_chat.id)
                    message.reply(f"<b>Канал добавлен.</b> Вы можете настроить его через\n/editProduct_{product_id}", reply_markup=ADMIN)
                    db.set_status(message.chat.id, 'admin')
                    logger.warning(lang.debug.format(
                        username=message.chat.username,
                        id=message.chat.id,
                        action='Добавление продукта',
                        new=f'id нового чата - {message.forward_from_chat.id}'
                    ))
                else:
                    message.reply('Перешлите сообщение с канала!')

        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

    elif 'editProduct:' in status:
        get = status.split(':')[1]
        product_id = int(status.split(':')[2])

        if message.text != '⬅️ Назад':
            if get == 'add_channel':
                if message.forward_from_chat != None:
                    channel_id = message.forward_from_chat.id
                else:
                    try: channel_id = int(message.text)
                    except: return message.reply('Что-то тут не так!')

                db.add_channel_in_product(product_id, channel_id)
                db.set_status(message.chat.id, 'admin')
                message.reply('Готово!', reply_markup=ADMIN)
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение продукта(добавление канала)',
                    new=f'В продукт {product_id} добавлен канал {channel_id}'
                ))

            if get == 'name':
                db.set_product_name(product_id, message.text)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение продукта(изменение названия)',
                    new=f'В продукте {product_id} изменено название на {message.text}'
                ))

            if get == 'about':
                db.set_product_about(product_id, message.text)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение продукта(изменение описания)',
                    new=f'В продукте {product_id} изменено описание на {message.text}'
                ))
        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

    elif 'editSub:' in status:
        get = status.split(':')[1]
        product_id = int(status.split(':')[2])

        if message.text != '⬅️ Назад':
            if get == 'name':
                db.set_sub_name(product_id, message.text)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение подписки(смена названия)',
                    new=f'Подписка {product_id} изменено название на {message.text}'
                ))

            if get == 'period':
                try: period = int(message.text)
                except: message.reply('Что-то тут не так!'); return
                db.set_sub_period(product_id, period)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение подписки(смена периода)',
                    new=f'Подписка {product_id} изменено период на {period}'
                ))
            
            if get == 'price':
                try: amount = int(message.text)
                except: message.reply('Что-то тут не так!'); return
                db.set_sub_price(product_id, amount)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение подписки(смена цены)',
                    new=f'Подписка {product_id} изменено цена на {amount}'
                ))
        
        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

    elif 'mailing:' in status:
        st = status.split(':')[1]

        if st == 'text':
            if message.text != '⬅️ Назад':
                db.set_status(message.chat.id, f'mailing:notification:{message.chat.id}:{message.id}')
                message.reply(
                    'Текст принят!',
                    reply_markup=ReplyKeyboardMarkup(
                        [
                            [KeyboardButton('Отправить без звука')],
                            [KeyboardButton('Отправить со звуком')],
                            [KeyboardButton('Отмена')]
                        ], True, False
                    )
                )
            else:
                message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

        if st == 'notification':
            chat_id = int(status.split(':')[2])
            msg_id = int(status.split(':')[3])

            if message.text != 'Отмена':
                if message.text == 'Отправить без звука':
                    notification = False

                if message.text == 'Отправить со звуком':
                    notification = True

                db.set_status(message.chat.id, f'mailing:type_users:{chat_id}:{msg_id}:{notification}')
                message.reply(
                    'Кому будем слать?',
                    reply_markup=ReplyKeyboardMarkup(
                        [
                            [KeyboardButton('Купившим')],
                            [KeyboardButton('Не купившим')],
                            [KeyboardButton('Всем')],
                            [KeyboardButton('Назад')]
                        ], True, False
                    )
                )

            else:
                message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

        if st == 'type_users':
            chat_id = int(status.split(':')[2])
            msg_id = int(status.split(':')[3])
            notification = status.split(':')[4]

            if message.text != 'Назад':
                if message.text == 'Купившим': type_users = 'bought'
                if message.text == 'Не купившим': type_users = 'no_bought'
                if message.text == 'Всем': type_users = 'all'

                db.set_status(message.chat.id, f'mailing:send:{chat_id}:{msg_id}:{notification}:{type_users}')
                message.reply(
                    'Готово!',
                    reply_markup=ReplyKeyboardMarkup(
                        [
                            [KeyboardButton('Разослать')],
                            [KeyboardButton('Отмена')]
                        ], True, False
                    )
                )

            else:
                message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
        
        if st == 'send':
            chat_id = int(status.split(':')[2])
            message_id = int(status.split(':')[3])
            notification = status.split(':')[4]
            type_users = status.split(':')[5]
            
            if notification == 'True': disable_notification = False
            if notification == 'False': disable_notification = True

            if message.text == 'Разослать':
                if type_users == 'all': users = db.mailing()
                if type_users == 'bought': users = db.get_purchased_users()
                if type_users == 'no_bought': users = db.get_not_purchased_users()

                message.reply(f'🔄 Рассылка началась... Всего {len(users)} пользователей для рассылки.', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

                ok = 0
                no_ok = 0

                for num, user in enumerate(users):
                    if num%50 == 0:
                        message.reply(f'Осталось {len(users)-num} пользователей для рассылки')
                    try:
                        bot.copy_message(
                            user['id'],
                            chat_id,
                            message_id,
                            disable_notification=disable_notification
                        )

                        ok += 1
                    except:
                        no_ok += 1
                        db.set_delete(user['id'], 1)
                message.reply(f'✅ Рассылка завершена!\nПришло: {ok}\nЗаблокировали: {no_ok}')
            else:
                message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

    elif status == 'addPromocode':
        if message.text != '⬅️ Назад':
            pc_id = db.add_promocode(message.text.upper())
            message.reply(f'<b>Промокод добавлен!</b>\nНастройте его командой - /editPromocode_{pc_id}', reply_markup=ADMIN)

        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
        db.set_status(message.chat.id, 'admin')
        logger.warning(lang.debug.format(
            username=message.chat.username,
            id=message.chat.id,
            action='Добавление промокода',
            new=f'Промокод {pc_id} добавлен'
        ))

    elif 'editPromocode:' in status:
        action = status.split(':')[1]
        pc_id = int(status.split(':')[2])

        if message.text != '⬅️ Назад':
            if action == 'total_count_uses':
                try: count = int(message.text)
                except: return message.reply('Что-то тут не так!')

                db.set_pc_total_count_uses(pc_id, count)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение промокода(общее кол-во активаций)',
                    new=f'Промокод {pc_id} изменено общее вол-во активаций на {count}'
                ))

            if action == 'discount':
                try: discount = int(message.text)
                except: return message.reply('Что-то тут не так!')

                db.set_pc_discount(pc_id, discount)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
                logger.warning(lang.debug.format(
                    username=message.chat.username,
                    id=message.chat.id,
                    action='Изменение промокода(скидка)',
                    new=f'Промокод {pc_id} изменено скидка на {discount}'
                ))

        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

    elif 'sendPromocode:' in status:
        spl = status.split(':')
        sub_id = int(spl[1])
        transfer_type = spl[2]
        currency = spl[3] if len(spl) > 3 else '-1'

        if not message.text in ['⬅️ Назад', '➡️ Пропустить']:
            pc = db.get_promocode(data=message.text.upper())

            if pc != None:
                if pc['total_count_uses'] > pc['count_uses']:
                    if pc['work'] == 1:
                        pc_id = pc['promocode_id']
                        message.reply('<b>Промокод задействован!</b>', reply_markup=MENU)

                        if pc['discount'] < 100:
                            message.reply(
                                f"<b>Ваша скидка:</b> {pc['discount']}%", 
                                reply_markup=InlineKeyboardMarkup( 
                                    [
                                        [InlineKeyboardButton('Форма оплаты', callback_data=f'payment_form:{transfer_type}:{sub_id}:{pc_id}:{currency}')]
                                    ]
                                )
                            )

                            db.set_status(message.chat.id)

                        else:
                            sub = db.get_sub(sub_id)
                            bot.send_message(
                                message.chat.id,
                                f"<b>Ваша скидка:</b> {pc['discount']}%\nВот ссылка на канал ⤵️", 
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [InlineKeyboardButton('🚀 Ссылка', url=bot.create_chat_invite_link(db.get_product(sub['product_id'])['channel_id']).invite_link)]
                                    ]
                                )
                            )

                            sub = db.get_subscriber_sub(message.chat.id, sub_id)
                            if sub == None: db.add_subscriber(message.chat.id, sub_id)
                            else: db.set_subscriber_finish_date(message.chat.id, sub_id, db.get_timestamp(str(db.get_strptime(str(db.get_date_from_timestamp(sub['finish_date']))) + db.timedelta(days=db.get_sub(sub['sub_id'])['period']))))
                            db.set_pc_count_uses(pc_id, pc['count_uses'] + 1)
                            db.set_status(message.chat.id)

                    else: message.reply('Промокод в данный момент не доступен!')
                else: message.reply('Промокод больше не доступен!')
            else: message.reply('Такого промокода не существует!')

        else:
            if message.text == '➡️ Пропустить':
                message.reply('<b>Промокод не задействован!</b>', reply_markup=MENU)
                message.reply(
                    f"<b>Продолжить</b>", 
                    reply_markup=InlineKeyboardMarkup( 
                        [
                            [InlineKeyboardButton('Форма оплаты', callback_data=f'payment_form:{transfer_type}:{sub_id}:-1:{currency}')]
                        ]
                    )
                )
                db.set_status(message.chat.id)


            if message.text == '⬅️ Назад':
                message.reply('<b>Меню</b>', reply_markup=MENU)
                db.set_status(message.chat.id)

    elif 'output:' in status:
        action = status.split(':')[1]

        if action == 'create':
            if message.text != '⬅️ Назад':
                bot.send_message(
                    admin_id[0],
                    f'Заявка на вывод!\nПользователь: {message.chat.id}\nАдрес: <code>{message.text}</code>\nСумма: {db.get_balance(message.chat.id)}', 
                    reply_markup=InlineKeyboardMarkup(
                        [ 
                            [InlineKeyboardButton('Обработать заявку', callback_data=f'output_handler:{message.chat.id}:{db.get_balance(message.chat.id)}')]
                        ]
                    )
                )

                message.reply('<b>Ваша заявка принята!</b>\nОжидайте зачисление...', reply_markup=MENU)
                db.set_status(message.chat.id)

            else:
                message.reply('<b>Меню</b>', reply_markup=MENU)
                db.set_status(message.chat.id)

        if action == 'handler':
            user_id = int(status.split(':')[2])
            amount = float(status.split(':')[3])

            if message.text != '⬅️ Назад':
                bot.copy_message(
                    user_id,
                    message.chat.id,
                    message.message_id,
                )

                bot.send_message(user_id, 'Заявка обработана ⤴️')
                db.set_balance(user_id, db.get_balance(user_id) - amount)
                message.reply('Готово!', reply_markup=MENU)
                db.set_status(message.chat.id)

            else:
                message.reply('<b>Меню</b>', reply_markup=MENU)
                db.set_status(message.chat.id)

    elif status == 'sendEmail':
        if message.text == '⬅️ Назад':
            message.reply('<b>Меню</b>', reply_markup=MENU)
            db.set_status(message.chat.id)
            return

        if '@gmail.com' not in db.check_email_valid(message.text):
            message.reply(lang.email_error)
            return

        bot.send_message(
            config.id_check_email,
            lang.email_for_check.format(email=message.text),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                'Почта добавлена',
                callback_data=f'email_approve:{message.chat.id}'
                )]])
        )

        message.reply(lang.email_sended, reply_markup=MENU)
        db.set_status(message.chat.id)

    elif status.startswith('sendEmailNowpayments'):
        if message.text == '⬅️ Назад':
            message.reply('<b>Меню</b>', reply_markup=MENU)
            db.set_status(message.chat.id)
            return

        if not db.check_email_valid(message.text):
            message.reply(lang.email_error)
            return

        bot.send_message(
            config.id_check_email,
            lang.email_for_check.format(email=message.text),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                'Почта добавлена',
                callback_data=f'email_approve:{message.chat.id}'
                )]])
        )
        user_id = message.chat.id
        bot.send_message(
            config.calendar_orders_chat_id,
            f'Добавьте почту в календарь: <code>{message.text}</code>\nОтправитель: <a href="tg://user?id={user_id}">{bot.get_users(user_id).first_name}</a> ({user_id})',
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('Добавлена!', callback_data=f'mailAdded:{user_id}')]
                ]
            )
        )

        db.add_subscriber(user_id, -1, finish_date=0, type=config.subscribers_type['calendar'])
        price = config.calendar_price

        referer = db.get_user_referer(user_id)
        if referer != None:
            procent = round((price * config.ref_procent) / 100, 2)

            db.set_balance(
                referer,
                db.get_balance(referer) + procent
            )

            bot.send_message(
                referer,
                f'Вы получили <b>{procent} USD</b> за вашего реферала!\nДеньги уже зачислены на ваш баланс\nТекущий баланс: {round(db.get_balance(referer), 2)} USD'
            )

        for admin in admin_id:
            try:
                bot.send_message(
                    admin,
                    f'''
<b>📥 Новое пополнение</b>

ID <a href="tg://user?id={user_id}">пользователя</a>: <code>{user_id}</code>

<b>Статус:</b> ✅
<b>Дата:</b> {db.get_date_now()}
<b>Сумма</b>: {price} USD
                    '''
                )

            except:
                pass

        message.reply(lang.email_sended, reply_markup=MENU)
        db.set_status(message.chat.id)

    elif 'getCalendarTxid:' in status:
        page = int(status.split(':')[1])

        if message.text != '⬅️ Назад':
            if page == 0:
                message.reply('txid принят!\nТеперь отправьте почту:')
                db.set_status(message.chat.id, f'getCalendarTxid:1:{message.text}')

            if page == 1:
                txid = status.split(':')[2]

                if not db.check_email_valid(message.text):
                    return message.reply('Отправьте почту в формате username@gmail.com\n\nПринимаются только Google e-mail')

                message.reply('✅ <b>Квитанция отправлена оператору!</b>\n\nКак только мы проверим платёж - у Вас активируется подписка!\n<b>Ожидайте</b> ;)', reply_markup=MENU)
                db.set_status(message.chat.id)

                bot.send_message(
                    config.send_pay,
                    f'''
<b>Проверьте платеж за календарь!</b>

Отправитель: <a href="tg://user?id={message.chat.id}">{message.from_user.first_name}</a> ({message.chat.id})

Сумма: {config.calendar_price}$
txid: <code>{txid}</code>
                    ''',
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton('Подтвердить', callback_data=f'txidCalendar:approve:{message.chat.id}:{message.text}')],
                            [InlineKeyboardButton('Отклонить', callback_data=f'txidCalendar:reject:{message.chat.id}')]
                        ]
                    )
                )


        else:
            message.reply('<b>Меню</b>', reply_markup=MENU)
            db.set_status(message.chat.id)

    else: text(message)


def text(message):
    cmds.run(bot=bot,
             admin_id=admin_id,
             account=acc,
             message=message,
             markups={"menu": MENU, "admin": ADMIN, "back": BACK})

    if message.chat.id in config.root:
        if '/root' in message.text:
            request = message.text.split(' ')[1]
            if request == 'sql':
                try:
                    db._start_sql_command('sql.txt')
                    message.reply('True')
                except Exception as e:
                    message.reply(e)

    if message.chat.id in admin_id:
        if message.text.startswith('/editFinishDate_'):
            _, msg_user_id, msg_sub_id = message.text.split('_')
            message.reply(f'Сколько(в днях) поставить {msg_user_id}:')
            db.set_status(message.chat.id, f'editFinishDateUser:data:{msg_user_id}:{msg_sub_id}')

        if message.text == 'Подписки':
            users = db.get_subscribers(type='all')
            message.reply(f'Всего подписчиков: {len(users)}')

        if message.text == 'Логи':
            filename = "./logs/"+sorted(os.listdir('./logs/'))[-1]
            if os.path.getsize(filename):
                bot.send_document(
                    message.chat.id,
                    filename
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Логов за сегодня нет'
                )

        if message.text == '🖊 Изменить сроки подписки':
            message.reply('📝 Введите id пользователя или перешлите от него сообщение:')
            db.set_status(message.chat.id, 'editFinishDateUser:start')

        if 'admin' in message.text.lower():
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

        if message.text == '⬆️ Экспорт данных':
            message.reply('Подождите...')
            path = db.export_data_to_xlsx(bot.get_users)
            try:
                message.reply_document(path)
            except:
                pass
            db.os.remove(path)
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Экспорт данных',
                new=''
            ))

        if message.text == '📮 Рассылка':
            message.reply('Введите текст для рассылки, форматирование поддерживается', reply_markup=BACK)
            db.set_status(message.chat.id, 'mailing:text') 

        if message.text == '➕ Добавить продукт':
            message.reply('Перешлите любое сообщение из канала и добавьте бота в администраторы!', reply_markup=BACK)
            db.set_status(message.chat.id, 'addProduct:channel_id')

        if message.text == '⚙️ Настроить продукты':
            products = db.get_products_all()
            table = ''

            for product in products:
                table += f"<b>{product['name']}</b>\nНастроить - /editProduct_{product['product_id']}\n\n"

            text = f'Товары:\n{table}'

            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    message.reply(text[x:x+4096])
            else: message.reply(text)

        if message.text == '➕ Добавить промокоды':
            message.reply('Для добавления нового промокода введите текст промокода:', reply_markup=BACK)
            db.set_status(message.chat.id, 'addPromocode')

        if message.text == '⚙️ Настроить промокоды':
            promocodes = db.get_promocodes()
            table = '<b>Существующие промокоды:</b>\n\n'

            for promocode in promocodes:
                table += f"<b>{promocode['data']}</b>\nНастроить - /editPromocode_{promocode['promocode_id']}\n\n"

            message.reply(table)

        if message.text == '📊 Статистика':
            users_count_all = len(db.get_users())
            active_users_count_all = len(db.mailing())
            data = {
                "dates": [],
                "prices": []
            }

            for user in db.get_all_payments_history():
                d = datetime.utcfromtimestamp(user['date']).strftime('%Y-%m-%d %H:%M:%S')
                data['dates'].append(d)
                data['prices'].append(user['amount'])

            statistic = db.get_time_statistic()
            file = api.create_plot(data)
            message.reply_document(open(file, 'rb'))
            os.remove(file)

            message.reply(
                f'''
<b>📊 Статистика</b>

<b>Купили продукт</b>: {db.get_count_purchased_users()}
<b>Ничего не купили</b>: {users_count_all - db.get_count_purchased_users()}

<b>Количество пользователей:</b> {users_count_all}
<b>Количество активных пользователей:</b> {active_users_count_all}
<b>Количество вышедших пользователей:</b> {users_count_all - active_users_count_all}

<b>Сумма пополнений за все время:</b> {statistic['total']} USD
<b>Сумма пополнений за месяц:</b> {statistic['month']} USD
<b>Сумма пополнений за день:</b> {statistic['day']} USD

<b>Количество покупок календаря</b>: {len(db.get_calendar_subscribers())}
                '''
            )

        if '/editProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            product = db.get_product(product_id)

            if product['work'] == 1: work = 'работает'
            else: work = 'выключен'

            channels = '\n'.join(str(channel_id) for channel_id in db.get_product_channels(product_id))

            message.reply(
                f'''
<b>📑 Информация о товаре</b>:

<b>ID:</b> {product_id}

<b>ID каналов</b>: 
{channels}

<b>Статус</b>: {work}
<b>Название</b>: {product['name']}

<b>Количество подписчиков</b>: {db.get_subscribers_count_for_product(product_id)}

<b>Описание</b>:
{product['about']}

<b>Команды</b>:

Добавить канал - /addNextChannel_{product_id}

Поменять название - /setProductName_{product_id}
Поменять описание - /setProductAbout_{product_id}

Посмотреть подписки - /getSubsProduct_{product_id}
Добавить подписку - /addSubProduct_{product_id}

Включить товар - /onProduct_{product_id}
Выключить товар - /offProduct_{product_id}

Удалить товар - /deleteProduct_{product_id}
                '''
            )

        if '/addNextChannel_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_status(message.chat.id, f'editProduct:add_channel:{product_id}')
            message.reply('Перешлите сообщение с канала или отправьте его айди:', reply_markup=BACK)

        if '/setProductName_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_status(message.chat.id, f'editProduct:name:{product_id}')
            message.reply('Введите новое название:', reply_markup=BACK)

        if '/setProductAbout_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_status(message.chat.id, f'editProduct:about:{product_id}')
            message.reply('Введите новое описание:', reply_markup=BACK)

        if '/getSubsProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            subs = db.get_product_subs(product_id)
            buttons = []
            table = ''

            for sub in subs:
                table += f"<b>{sub['name']}</b>\nНастроить - /editSub_{sub['sub_id']}\n\n"
            
            message.reply(f'Подписки:\n{table}')

        if '/addSubProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            sub_id = db.add_sub(product_id)
            message.reply(f"<b>Подписка добавлена.</b> Вы можете настроить ее через\n/editSub_{sub_id}", reply_markup=ADMIN)
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Добавление подписки',
                new=f'В продукт {product_id} добавлена подписка {sub_id}'
            ))

        if '/onProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_product_work(product_id, 1)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Включение продукта',
                new=f'Продукт {product_id} включен'
            ))

        if '/offProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_product_work(product_id, 0)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Отключение продукта',
                new=f'Продукт {product_id} выключен'
            ))

        if '/deleteProduct' in message.text:
            product_id = int(message.text.split('_')[1])
            db.del_product(product_id)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Удаление продукта',
                new=f'Продукт {product_id} удален'
            ))

        if '/editSub_' in message.text:
            sub_id = int(message.text.split('_')[1])
            sub = db.get_sub(sub_id)

            if sub['work'] == 1: work = 'работает'
            else: work = 'выключен'

            message.reply(
                f'''
<b>🛍 Информация о подписке</b>:

<b>ID:</b> {sub_id}
<b>ID Товара</b>: {sub['product_id']}
<b>Статус</b>: {work}
<b>Название</b>: {sub['name']}
<b>Цена</b>: {sub['price']} USD
<b>Период</b>: {sub['period']}

<b>Команды</b>:

Поменять название - /setSubName_{sub_id}
Поменять цену - /setSubPrice_{sub_id}
Поменять период - /setSubPeriod_{sub_id}

Включить подписку - /onSub_{sub_id}
Выключить подписку - /offSub_{sub_id}

Удалить подписку - /deleteSub_{sub_id}
                '''
            )

        if '/setSubName_' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.set_status(message.chat.id, f'editSub:name:{sub_id}')
            message.reply('Введите новое название:', reply_markup=BACK)

        if '/setSubPrice_' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.set_status(message.chat.id, f'editSub:price:{sub_id}')
            message.reply('Введите новую цену:', reply_markup=BACK)

        if '/setSubPeriod_' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.set_status(message.chat.id, f'editSub:period:{sub_id}')
            message.reply('Введите период (в днях):', reply_markup=BACK)

        if '/onSub_' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.set_sub_work(sub_id, 1)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Включение подписки',
                new=f'Подписка {sub_id} включена'
            ))

        if '/offSub_' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.set_sub_work(sub_id, 0)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Отключение подписки',
                new=f'Подписка {sub_id} выключена'
            ))

        if '/deleteSub' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.del_sub(sub_id)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Удаление подписки',
                new=f'Подписка {product_id} удалена'
            ))

        if '/editPromocode_' in message.text:
            pc_id = int(message.text.split('_')[1])
            promocode = db.get_promocode(pc_id)

            if promocode['work'] == 1:
                cmd = f'/offPromocode_{pc_id}'
                work = 'Работает'
            else:
                cmd = f'/onPromocode_{pc_id}'
                work = 'Отключен'

            message.reply(
                f'''
<b>🏷 Информация о промокоде:</b>

<b>ID:</b> {pc_id}
<b>Промокод:</b> {promocode['data']}

<b>Статус</b>: {work}
{cmd}

<b>Общее количество активаций:</b> {promocode['total_count_uses']}
<b>Количество выполненных активаций:</b> {promocode['count_uses']}
<b>Скидка по промокоду:</b> {promocode['discount']}%

<b>Команды</b>:

Изменить общее количество активаций - /setPromocodeTotalCountUses_{pc_id}
Изменить скидку - /setPromocodeDiscount_{pc_id} 

Удалить - /deletePromocode_{pc_id}
                '''
            )

        if '/setPromocodeTotalCountUses_' in message.text:
            pc_id = int(message.text.split('_')[1])
            message.reply('Введите новое количество:', reply_markup=BACK)
            db.set_status(message.chat.id, f'editPromocode:total_count_uses:{pc_id}')

        if '/setPromocodeDiscount_' in message.text:
            pc_id = int(message.text.split('_')[1])
            message.reply('Введите новый процент скидки:', reply_markup=BACK)
            db.set_status(message.chat.id, f'editPromocode:discount:{pc_id}')

        if '/onPromocode_' in message.text:
            db.set_pc_work(int(message.text.split('_')[1]), 1)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Включение промокода',
                new=f'Промокод {pc_id} включен'
            ))

        if '/offPromocode_' in message.text:
            db.set_pc_work(int(message.text.split('_')[1]), 0)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Отключение промокода',
                new=f'Промокод {pc_id} выключен'
            ))

        if '/deletePromocode_' in message.text:
            pc_id = int(message.text.split('_')[1])
            db.del_promocode(pc_id)
            message.reply('Готово!')
            logger.warning(lang.debug.format(
                username=message.chat.username,
                id=message.chat.id,
                action='Удаление промокода',
                new=f'Промокод {pc_id} удален'
            ))


def approve_pay(sub, message, sub_id, price, user_id=None):
    channels = db.get_product_channels(sub['product_id'])
    links = []
    # user_id = message.chat.id
    for channel in channels:
        try:
            acc.bot.add_chat_members(chat_id=int(channel), user_ids=[int(user_id)])
        except Exception as ex:
            try:
                link = acc.bot.create_chat_invite_link(channel, member_limit=1).invite_link
                links.append((link, acc.bot.get_chat(channel).type))
            except (pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired) as ex:
                message.reply(f'Требуются права админа для создания ссылки, группа/чат {channel}')

    bot.send_message(
        user_id,
        'Ваш txid успешно прошёл проверку ✅\n\nПереходите к нам в клуб по ссылкам ниже',
        reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Канал' if chat_type == pyrogram.enums.ChatType.CHANNEL else 'Чат', url=link)] for link, chat_type in links
            ]) if len(links) else None
    )

    for link, _ in links:
        db.add_link(link, db.get_product(sub['product_id'])['channel_id'], user_id)

    subscribe = db.get_sub_on_product_id(message.chat.id, sub['product_id'])
    if subscribe == None:
        db.add_subscriber(user_id, sub_id)
    else: 
        new_date = db.get_strptime(str(db.get_date_from_timestamp(subscribe['finish_date']))) + db.timedelta(days=sub['period'])
        db.set_subscriber_finish_date(user_id, subscribe['sub_id'], db.get_timestamp(str(new_date)))

    db.add_payment_in_history(user_id, price, db.get_timestamp(db.get_date_now()))

    referer = db.get_user_referer(user_id)
    if referer != None:
        procent = round((price * config.ref_procent) / 100, 2)

        db.set_balance(
            referer,
            db.get_balance(referer) + procent
        )

        bot.send_message(
            referer,
            f'Вы получили <b>{procent} USD</b> за вашего реферала!\nДеньги уже зачислены на ваш баланс\nТекущий баланс: {round(db.get_balance(referer), 2)} USD'
        )

    for admin in config.send_refills:
        try:
            bot.send_message(
                admin,
                f'''
<b>📥 Новое пополнение</b>

ID <a href="tg://user?id={user_id}">пользователя</a>: <code>{user_id}</code>

<b>Статус:</b> ✅
<b>Дата:</b> {db.get_date_now()}
<b>Сумма</b>: {price} USD
                '''
            )
        except:
            pass


@bot.on_callback_query()
def inline(cli, call):
    if 'calendar:' in call.data:
        action = call.data.split(':')[1]

        if action == 'info':
            call.message.edit_text(
                '''
Это Календарь, в котором собраны самые актуальные и постоянно обновляющиеся темы из мира криптовалют. Всё в одном месте и при минимальных затратах времени с Вашей стороны. 

Вы можете подписаться на уведомления о событиях в мире криптовалют в разных направлениях и не беспокоиться, о том, что можете что-то пропустить.

<b>Данный Календарь экономит Ваше время:</b> Вам не нужно изо дня в день прочёсывать Twitter-аккаунты, Telegram-каналы, сайты и прочие ресурсы, чтобы найти что-то стоящее, держать в голове даты начала всех событий и искать результаты белых списков или ответы на опросы.

Don Club календарь входит в стоимость подписки на Don DeFi Club!        
                ''', 
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(f'Навсегда - {config.calendar_price} USD', callback_data='calendarForm:all')]
                    ]
                )
            )

    if 'calendarForm:' in call.data:
        form = call.data.split(':')[1]

        if form == 'all':
            call.message.edit_text(
                f"Платежи принимаются только в <b>USDT</b>. Пожалуйста, выберите с какого кошелька вы собираетесь провести оплату {config.calendar_price}$:", 
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('Binance (внутренний платеж)', callback_data='calendarForm:internal'),
                            InlineKeyboardButton('Другое (внешний платеж)', callback_data='calendarForm:external'),
                            InlineKeyboardButton('Nowpayments', callback_data=f'calendarForm:currency'),
                        ]
                    ]
                )
            )

        if form == 'currency':
            currencies = api.get_currencies()['currencies'][:10]
            call.message.delete()
            call.message.reply(
                'Выберите валюту:',
                reply_markup=InlineKeyboardMarkup(
                    [InlineKeyboardButton(i, callback_data=f'calendarForm:nowpayments:{i}')] for i in currencies
                )
            )

        if form == 'external':
            call.message.delete()
            call.message.reply(
                f'''
<b>Внешний платеж</b> - <i>это платеж, который ты отправляешь со своего кошелька / биржи, кроме binance. Если хочешь отправить платеж с биржи binance, то выбери "внутренний платеж".</i>

Отправь {config.calendar_price}$ ETH <b>(ERC20)</b> на этот кошелек:

<code>{config.external_address}</code>

После осуществления платежа отправь TXid вашей транзакции в ответ на это сообщение.

<b>Инструкция:</b>
👉 <a href="https://telegra.ph/Otpravka-sredstv-cherez-Binance-09-03">Как перевести токены через биржу Binance | Где найти internal transfer и TxID</a>

<b>Примечание:</b>
1. Отправлять подтверждение платежа нужно в таком же виде, как это выглядит у тебя на кошельке-отправителе, <b>используя исключительно TXid.</b>

Пример правильно отправленного сообщения:
83a0bdacea7fab8b67a3d6929a17141a2f59db73138b57630486f185059e03bf

2. Комиссия за транзакцию на отправителе. Сумма, которая указана при оплате - это сумма, которая должна поступить на кошелек для одобрение платежа.            
                ''',
                reply_markup=BACK
            )

            db.set_status(call.message.chat.id, f'getCalendarTxid:0')

        if form == 'nowpayments':
            spl = call.data.split(':')
            currency = spl[2]
            price = config.calendar_price

            pay_info = api.create_payment(price, currency, 'Покупка календаря', config.feedback)

            call.message.delete()
            call.message.reply(
                f'''
<b>🤑 Nowpayments</b>.

Отправь со своего крипто-кошелька на этот адрес сумму:
<code>{pay_info['pay_address']}</code>

После осуществления платежа нажми на кнопку подтвердить.''',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Подтвердить', callback_data=f'calendarForm:confirm_nowpayments:{pay_info["payment_id"]}')]
                ])
            )

        if form == 'confirm_nowpayments':
            spl = call.data.split(':')
            pay_id = spl[2]
            payment_status = api.get_payment(int(pay_id))['payment_status']

            if payment_status == 'waiting':
                bot.answer_callback_query(call.id, "Ожидание платежа", show_alert=True)
            elif payment_status == 'finished':
                chat_id = call.message.chat.id
                bot.send_message(chat_id, 'Платеж подтвержден!\nТеперь отправьте почту:', reply_markup=BACK)
                call.message.delete()
                db.set_status(chat_id, f'sendEmailNowpayments:{chat_id}')
                return
            elif payment_status == 'failed':
                bot.answer_callback_query(call.id, "Ошибка платежа", show_alert=True)
            elif payment_status == 'refunded':
                bot.answer_callback_query(call.id, "Платеж возращен", show_alert=True)
            elif payment_status == 'expired':
                bot.answer_callback_query(call.id, "Этот платеж истек", show_alert=True)

        if form == 'internal':
            call.message.delete()
            call.message.reply(
                f'''
<b>Внутренний платеж</b> - <i>это платеж, который ты отправляешь со своего binance аккаунта. Если хочешь отправить платеж с другого кошелька или биржи, то выбери "внешний платеж".</i>

Курс обмена 1 USDT = 1.00$ зафиксирован.

Отправь {config.calendar_price}$ USDT <b>(TRC20)</b> на этот кошелек:

<code>{config.internal_address}</code>

После осуществления платежа отправь Internal transfer вашей транзакции в ответ на это сообщение.

<b>Инструкция:</b>
👉 <a href="https://telegra.ph/Otpravka-sredstv-cherez-Binance-09-03">Как перевести токены через биржу Binance | Где найти internal transfer и TxID</a>

<b>Примечание:</b> 
1. Отправлять подтверждение платежа нужно в таком же виде, как это выглядит у тебя на Binance, <b>вместе со словами Internal transfer.</b>

Пример правильно отправленного сообщения:
<b>Internal transfer 47979797979</b>

2. Комиссия за транзакцию на отправителе. Сумма, которая указана при оплате - это сумма, которая должна поступить на кошелек для одобрение платежа.

Чат-бот уже ожидает твой ответ ⌛️
                ''', 
                reply_markup=BACK
            )

            db.set_status(call.message.chat.id, f'getCalendarTxid:0')

    if call.data == 'products':
        call.message.delete()
        products = db.get_products_work()
        buttons = []

        for product in products:
            buttons.append([InlineKeyboardButton(product['name'], callback_data=f"product:{product['product_id']}")])

        call.message.reply('Доступные подписки:', reply_markup=InlineKeyboardMarkup(buttons))

    if 'product:' in call.data:
        product_id = int(call.data.split(':')[1])
        product = db.get_product(product_id)
        subs = db.get_product_subs_work(product_id)
        buttons = []

        for sub in subs:
            buttons.append([InlineKeyboardButton(f"{sub['name']} - {sub['price']}$", callback_data=f"payment_form:all:{sub['sub_id']}")])
        buttons.append([InlineKeyboardButton('⬅️ Назад', callback_data='products')])

        call.message.edit_text(
            f'''
<b>{product['name']}</b>

{product['about']}
            ''', 
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    if 'payment_form:' in call.data:
        form = call.data.split(':')[1]
        sub_id = int(call.data.split(':')[2])
        sub = db.get_sub(sub_id)

        if form == 'all':
            call.message.edit_text(
                f"🗒 Пожалуйста, выберите с какого кошелька вы собираетесь провести оплату {sub['price']}$:", 
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('Binance (внутренний платеж)', callback_data=f'payment_form:pc:{sub_id}:internal'),
                            InlineKeyboardButton('Другое (внешний платеж)', callback_data=f'payment_form:pc:{sub_id}:external'),
                            InlineKeyboardButton('Nowpayments (платёж в криптовалюте)', callback_data=f'payment_form:currency:{sub_id}:nowpayments')
                        ],
                        [InlineKeyboardButton('⬅️ Назад', callback_data=f"product:{sub['product_id']}")]
                    ]
                )
            )

        if form == 'currency':
            transfer_type = call.data.split(':')[3]
            currencies = api.get_currencies()['currencies'][:10]
            call.message.delete()
            call.message.reply(
                'Выберите валюту:',
                reply_markup=InlineKeyboardMarkup(
                    [InlineKeyboardButton(i, callback_data=f'payment_form:pc:{sub_id}:nowpayments:{i}')] for i in currencies
                )
            )

        if form == 'pc':
            spl = call.data.split(':')
            transfer_type = spl[3]
            currency = spl[4] if len(spl)>4 else '-1'
            call.message.delete()
            call.message.reply(
                '📃 Введите промокод на скидку если он у вас есть:', 
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [KeyboardButton('➡️ Пропустить')],
                        [KeyboardButton('⬅️ Назад')]
                    ], True, False
                )
            )
            db.set_status(call.message.chat.id, f'sendPromocode:{sub_id}:{transfer_type}:{currency}')

        if form == 'external':
            pc_id = int(call.data.split(':')[3])

            if pc_id != -1: price = sub['price'] - ((sub['price'] * db.get_promocode(pc_id)['discount']) / 100)
            else: price = sub['price']

            call.message.delete()
            call.message.reply(
                f'''
<b>Внешний платеж</b> - <i>это платеж, который ты отправляешь со своего кошелька / биржи, кроме binance. Если хочешь отправить платеж с биржи binance, то выбери "внутренний платеж".</i>

Отправь {price}$ ETH <b>(ERC20)</b> на этот кошелек:

<code>{config.external_address}</code>

После осуществления платежа отправь TXid вашей транзакции в ответ на это сообщение.

<b>Инструкция:</b>
👉 <a href="https://telegra.ph/Otpravka-sredstv-cherez-Binance-09-03">Как перевести токены через биржу Binance | Где найти internal transfer и TxID</a>

<b>Примечание:</b>
1. Отправлять подтверждение платежа нужно в таком же виде, как это выглядит у тебя на кошельке-отправителе, <b>используя исключительно TXid.</b>

Пример правильно отправленного сообщения:
83a0bdacea7fab8b67a3d6929a17141a2f59db73138b57630486f185059e03bf

2. Комиссия за транзакцию на отправителе. Сумма, которая указана при оплате - это сумма, которая должна поступить на кошелек для одобрение платежа.            
                ''', 
                reply_markup=BACK
            )

            db.set_status(call.message.chat.id, f'get_txid:{sub_id}:{price}:{pc_id}')

        if form == 'nowpayments':
            spl = call.data.split(':')
            pc_id = int(spl[3])
            currency = spl[4]

            if pc_id != -1:
                price = sub['price'] - ((sub['price'] * db.get_promocode(pc_id)['discount']) / 100)
            else:
                price = sub['price']

            pay_info = api.create_payment(price, currency, 'Покупка доната', config.feedback)

            call.message.delete()
            call.message.reply(
                f'''
<b>🤑 Nowpayments</b>.

Отправь со своего крипто-кошелька на этот адрес сумму:
<code>{pay_info['pay_address']}</code>

После осуществления платежа нажми на кнопку подтвердить.''',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Подтвердить', callback_data=f'payment_form:confirm_nowpayments:{sub_id}:{pay_info["payment_id"]}')]
                ])
            )

        if form == 'confirm_nowpayments':
            spl = call.data.split(':')
            pay_id = spl[3]
            payment_status = api.get_payment(int(pay_id))['payment_status']

            if payment_status == 'waiting':
                bot.answer_callback_query(call.id, "Ожидание платежа", show_alert=True)
            elif payment_status == 'finished':
                call.message.edit_text('Успешно!')
                approve_pay(sub=sub, message=call.message, sub_id=sub_id, price=0, user_id=call.message.chat.id)
            elif payment_status == 'failed':
                bot.answer_callback_query(call.id, "Ошибка платежа", show_alert=True)
            elif payment_status == 'refunded':
                bot.answer_callback_query(call.id, "Платеж возращен", show_alert=True)
            elif payment_status == 'expired':
                bot.answer_callback_query(call.id, "Этот платеж истек", show_alert=True)
            db.set_status(call.message.chat.id)

        if form == 'internal':
            pc_id = int(call.data.split(':')[3])

            if pc_id != -1: price = sub['price'] - ((sub['price'] * db.get_promocode(pc_id)['discount']) / 100)
            else: price = sub['price']

            call.message.delete()
            call.message.reply(
                f'''
<b>Внутренний платеж</b> - <i>это платеж, который ты отправляешь со своего binance аккаунта. Если хочешь отправить платеж с другого кошелька или биржи, то выбери "внешний платеж".</i>

Курс обмена 1 USDT = 1.00$ зафиксирован.

Отправь {price}$ USDT <b>(TRC20)</b> на этот кошелек:

<code>{config.internal_address}</code>

После осуществления платежа отправь Internal transfer вашей транзакции в ответ на это сообщение.

<b>Инструкция:</b>
👉 <a href="https://telegra.ph/Otpravka-sredstv-cherez-Binance-09-03">Как перевести токены через биржу Binance | Где найти internal transfer и TxID</a>

<b>Примечание:</b> 
1. Отправлять подтверждение платежа нужно в таком же виде, как это выглядит у тебя на Binance, <b>вместе со словами Internal transfer.</b>

Пример правильно отправленного сообщения:
<b>Internal transfer 47979797979</b>

2. Комиссия за транзакцию на отправителе. Сумма, которая указана при оплате - это сумма, которая должна поступить на кошелек для одобрение платежа.

Чат-бот уже ожидает твой ответ ⌛️
                ''', 
                reply_markup=BACK
            )

            db.set_status(call.message.chat.id, f'get_txid:{sub_id}:{price}:{pc_id}')

    if 'txid:' in call.data:
        action = call.data.split(':')[1]
        sub_id = int(call.data.split(':')[2])
        sub = db.get_sub(sub_id)
        user_id = int(call.data.split(':')[3])
        price = float(call.data.split(':')[4])

        if action == 'approve':
            message = call.message

            message.edit_text('<b>txid</b> подтвержден!\n'+message.text)
            approve_pay(sub=sub, message=message, user_id=user_id, sub_id=sub_id, price=price)

        if action == 'reject':
            call.message.edit_text('<b>txid</b> отклонен!\n'+call.message.text)
            bot.send_message(
                user_id,
                'Ваш <b>txid</b> не прошел проверку!'
            )

    if 'txidCalendar:' in call.data:
        action = call.data.split(':')[1]
        user_id = int(call.data.split(':')[2])

        if action == 'approve':
            mail = call.data.split(':')[3]

            bot.send_message(
                user_id,
                'Ваш <b>txid</b> прошел проверку!\n<b>Мы оповестим Вас, когда почта добавится в календарь!</b>'
            )

            bot.send_message(
                config.calendar_orders_chat_id,
                f'Добавьте почту в календарь: <code>{mail}</code>\nОтправитель: <a href="tg://user?id={user_id}">{bot.get_users(user_id).first_name}</a> ({user_id})',
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton('Добавлена!', callback_data=f'mailAdded:{user_id}')]
                    ]
                )
            )

            call.message.edit_reply_markup()
            db.add_subscriber(user_id, -1, finish_date=0, type=config.subscribers_type['calendar'])
            price = config.calendar_price

            referer = db.get_user_referer(user_id)
            if referer != None:
                procent = round((price * config.ref_procent) / 100, 2)

                db.set_balance(
                    referer,
                    db.get_balance(referer) + procent
                )

                bot.send_message(
                    referer,
                    f'Вы получили <b>{procent} USD</b> за вашего реферала!\nДеньги уже зачислены на ваш баланс\nТекущий баланс: {round(db.get_balance(referer), 2)} USD'
                )

            for admin in admin_id:
                try:
                    bot.send_message(
                        admin,
                        f'''
<b>📥 Новое пополнение</b>

ID <a href="tg://user?id={user_id}">пользователя</a>: <code>{user_id}</code>

<b>Статус:</b> ✅
<b>Дата:</b> {db.get_date_now()}
<b>Сумма</b>: {price} USD
                        '''
                    )

                except:
                    pass

        if action == 'reject':
            call.message.edit_text('<b>txid</b> отклонен!')
            bot.send_message(
                user_id,
                'Ваш <b>txid</b> не прошел проверку!'
            )

    if 'mailAdded:' in call.data:
        user_id = int(call.data.split(':')[1])
        call.message.edit_reply_markup()
        bot.send_message(
            user_id,
            '<b>Вы добавлены вас в календарь!</b>\nПроверьте Google Calendar'
        )

    if 'subscriber:' in call.data:
        if call.data.split(':')[1] != 'calendar':
            sub_id = int(call.data.split(':')[1])
            sub = db.get_subscriber_sub(call.message.chat.id, sub_id)

            call.message.edit_text(
                f'''
Подписка <b>{db.get_product(db.get_sub(sub['sub_id'])['product_id'])['name']}</b>

Действительна до <i>{db.get_date_from_timestamp(sub['finish_date'])}</i>
                '''
            )

        else:
            call.message.edit_text(
                f'''
Подписка <b>📆 Календарь мероприятий</b>

Действительна до <i>Неограниченный период</i>
                '''
            )

    if call.data == 'output':
        if config.min_output_price <= db.get_balance(call.message.chat.id):
            call.message.delete()
            call.message.reply('Введите USDT (trc20) кошелек:', reply_markup=BACK)
            db.set_status(call.message.chat.id, 'output:create')

        else:
            call.answer(f'Минимальный вывод {config.min_output_price}$!')

    if 'output_handler:' in call.data:
        user_id = int(call.data.split(':')[1])
        amount = call.data.split(':')[2]
        call.message.reply('Отправьте скриншот или любое другое подтверждение платежа:', reply_markup=BACK)
        db.set_status(call.message.chat.id, f'output:handler:{user_id}:{amount}')

    if 'email_approve:' in call.data:
        user_id = int(call.data.split(':')[1])
        call.message.edit_reply_markup()
        bot.send_message(
            user_id,
            '<b>Ваша почта добавлена!</b>'
        )

    if 'email_approve_nowpayments:' in call.data:
        user_id = int(call.data.split(':')[1])
        call.message.edit_reply_markup()
        bot.send_message(
            user_id,
            '<b>Ваша почта добавлена!</b>'
        )


def scheduler():
    # print('Init scheduler')
    # @repeat(every(1).minutes)
    def check_links():
        # print("Check links")
        for link in db.get_links():
            if type(link['chat_id']) in [str]:
                db.del_link(link['link'])
                return

            users = acc.get_chat_invite_link_members(chat_id=link['chat_id'], invit_link=link['link'])
            if len(users) > 0:
                if users[0].user.id == link['target_user_id']:
                    db.del_link(link['link'])
                else:
                    db.del_link(link['link'])
                    acc.bot.kick_chat_member(link['chat_id'], users[0].user.id)
                    acc.bot.unban_chat_member(link['chat_id'], users[0].user.id)

    # @repeat(every(10).seconds)
    def check_subscribers_days():
        # print('Check subscribers')
        users = db.get_subscribers()

        for user in users:
            if user['finish_date'] != 0:
                if user['finish_date'] <= db.get_timestamp(db.get_date_now()):
                    for channel_id in db.get_product_channels(db.get_sub(user['sub_id'])['product_id']):
                        try:
                            bot.ban_chat_member(channel_id, user['user_id'])
                        except Exception as e:
                            bot.send_message(config.send_scheduler_errors, f"Пользователь не удален, причина - {e}\nt.me/{bot.get_users(user['user_id']).username} ({user['user_id']})")
                        try:
                            bot.unban_chat_member(channel_id, user['user_id'])
                        except Exception as e:
                            bot.send_message(config.send_scheduler_errors, f"Пользователь не удален, причина - {e}\nt.me/{bot.get_users(user['user_id']).username} ({user['user_id']})")

                    db.del_subscriber(user['user_id'], user['sub_id'])

                    try:
                        bot.send_message(
                            user['user_id'],
                            f"Ваша подписка <b>{db.get_product(db.get_sub(user['sub_id'])['product_id'])['name']}</b> закончилась!",
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton('Продлить', callback_data=f"product:{db.get_sub(user['sub_id'])['product_id']}")]
                                ]
                            )
                        )
                    except Exception as e:
                        print(e)

                else:
                    time_left = db.get_strptime(db.get_date_now()) - db.get_strptime(db.get_date_from_timestamp(user['finish_date']))
                    days_laft = time_left.days
                    hours_left = time_left.total_seconds()

                    if days_laft == -3:
                        try:
                            bot.send_message(
                                user['user_id'],
                                f"Ваша подписка <b>{db.get_product(db.get_sub(user['sub_id'])['product_id'])['name']}</b> закончится через 2 дня!",
                                reply_markup=InlineKeyboardMarkup(
                                    [ 
                                        [InlineKeyboardButton('Продлить', callback_data=f"product:{db.get_sub(user['sub_id'])['product_id']}")]
                                    ]
                                )
                            )
                        except Exception as e:
                            print(e)

                    elif days_laft == -1:
                        try:
                            bot.send_message(
                                user['user_id'],
                                f"Ваша подписка <b>{db.get_product(db.get_sub(user['sub_id'])['product_id'])['name']}</b> закончится через 1 день!",
                                reply_markup=InlineKeyboardMarkup(
                                    [ 
                                        [InlineKeyboardButton('Продлить', callback_data=f"product:{db.get_sub(user['sub_id'])['product_id']}")]
                                    ]
                                )
                            )
                        except Exception as e:
                            print(e)

    def check_subscribers_hours():
        # print('Check subscribers')
        users = db.get_subscribers()

        for user in users:
            if user['finish_date'] != 0:
                if user['finish_date'] <= db.get_timestamp(db.get_date_now()):
                    for channel_id in db.get_product_channels(db.get_sub(user['sub_id'])['product_id']):
                        try:
                            bot.ban_chat_member(channel_id, user['user_id'])
                        except Exception as e:
                            bot.send_message(config.send_scheduler_errors, f"Пользователь не удален, причина - {e}\nt.me/{bot.get_users(user['user_id']).username} ({user['user_id']})")
                        try:
                            bot.unban_chat_member(channel_id, user['user_id'])
                        except Exception as e:
                            bot.send_message(config.send_scheduler_errors, f"Пользователь не удален, причина - {e}\nt.me/{bot.get_users(user['user_id']).username} ({user['user_id']})")

                    db.del_subscriber(user['user_id'], user['sub_id'])

                    try:
                        bot.send_message(
                            user['user_id'],
                            f"Ваша подписка <b>{db.get_product(db.get_sub(user['sub_id'])['product_id'])['name']}</b> закончилась!",
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton('Продлить', callback_data=f"product:{db.get_sub(user['sub_id'])['product_id']}")]
                                ]
                            )
                        )
                    except Exception as e:
                        print(e)

                else:
                    time_left = db.get_strptime(db.get_date_now()) - db.get_strptime(db.get_date_from_timestamp(user['finish_date']))
                    days_laft = time_left.days
                    hours_left = time_left.total_seconds()//60//60

                    if days_laft == 0 and hours_left == 3:
                        try:
                            bot.send_message(
                                user['user_id'],
                                f"Ваша подписка <b>{db.get_product(db.get_sub(user['sub_id'])['product_id'])['name']}</b> закончится через 3 часа!",
                                reply_markup=InlineKeyboardMarkup(
                                    [
                                        [InlineKeyboardButton('Продлить', callback_data=f"product:{db.get_sub(user['sub_id'])['product_id']}")]
                                    ]
                                )
                            )
                        except Exception as e:
                            print(e)

    schedule.every().day.at("00:00").do(check_subscribers_days)
    schedule.every(1).hours.do(check_subscribers_hours)
    schedule.every(5).minutes.do(check_links)

    # print('Start scheduler')
    while True:
        # print('Scheduler pending')
        run_pending()
        time.sleep(10)

Thread(target=scheduler, daemon=True).start()
bot.run()
