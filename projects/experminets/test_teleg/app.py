from pyrogram import (
    Client,
    filters
    )
from pyrogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
    )

import schedule
from threading import Thread
from time import sleep

import config
import db
from traceback import format_exc
from account import Account

bot = Client(
    'bot',
    api_id=18936848,
    api_hash="4da77bed845aebdfeceb62e83533d7f0",
    bot_token="5488863430:AAFsNYw_eaFQPr-eyR3B3O8-i8LsVUDrz2g"
)

admin_id = config.admin_id
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

    if message.text == '/restart':
        db.set_status(message.chat.id)
        message.reply('<b>Меню</b>', reply_markup=MENU)

    status = db.get_status(message.chat.id)
    # print(status)

    if status is None:
        text(message)
        return

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
                config.admin_id[0],
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

            if get == 'name':
                db.set_product_name(product_id, message.text)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

            if get == 'about':
                db.set_product_about(product_id, message.text)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
        
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

            if get == 'period':
                try: period = int(message.text)
                except: message.reply('Что-то тут не так!'); return
                db.set_sub_period(product_id, period)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
            
            if get == 'price':
                try: amount = int(message.text)
                except: message.reply('Что-то тут не так!'); return
                db.set_sub_price(product_id, amount)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')
        
        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

    elif 'mailing:' in status:
        st = status.split(':')[1]

        if st == 'text':
            if message.text != '⬅️ Назад':
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

                db.set_status(message.chat.id, f'mailing:notification:{message.chat.id}:{message.message_id}')

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

                message.reply('🔄 Рассылка началась...', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

                ok = 0
                no_ok = 0

                for user in users:
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
            db.set_status(message.chat.id, 'admin')

        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

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

            if action == 'discount':
                try: discount = int(message.text)
                except: return message.reply('Что-то тут не так!')

                db.set_pc_discount(pc_id, discount)
                message.reply('<b>Готово!</b>', reply_markup=ADMIN)
                db.set_status(message.chat.id, 'admin')

        else:
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

    elif 'sendPromocode:' in status:
        sub_id = int(status.split(':')[1])
        transfer_type = status.split(':')[2]

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
                                        [InlineKeyboardButton('Форма оплаты', callback_data=f'payment_form:{transfer_type}:{sub_id}:{pc_id}')]
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
                            [InlineKeyboardButton('Форма оплаты', callback_data=f'payment_form:{transfer_type}:{sub_id}:-1')]
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
        if message.text != '⬅️ Назад':
            if '@gmail.com' in db.check_email_valid(message.text):
                bot.send_message(
                    admin_id[0],
                    f'<b>Почта для проверки!</b>\nАдрес: <code>{message.text}</code>',
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton('Почта добавлена', callback_data=f'email_approve:{message.chat.id}')]
                        ]
                    )
                )

                message.reply('<b>Почта отправлена!</b> Мы сообющим когда она будет добавлена', reply_markup=MENU)
                db.set_status(message.chat.id)

            else:
                message.reply('Отправьте почту в формате username@gmail.com\n\nПринимаются только Google e-mail')

        else:
            message.reply('<b>Меню</b>', reply_markup=MENU)
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
                    config.admin_id[0],
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
    if message.chat.id in config.root:
        if '/root' in message.text:
            request = message.text.split(' ')[1]
            if request == 'sql':
                try:
                    db._start_sql_command('sql.txt')
                    message.reply('True')
                except Exception as e:
                    message.reply(e)

    if 'start' in message.text:
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

        message.reply(f'Привет, {message.from_user.first_name}! Здесь ты можешь купить подписку в Don | Invest Club!', reply_markup=MENU)

    if message.text == '🛍 Магазин':
        products = db.get_products_work()
        buttons = []

        for product in products:
            buttons.append([InlineKeyboardButton(product['name'], callback_data=f"product:{product['product_id']}")])

        buttons.append([InlineKeyboardButton("📆 Календарь мероприятий", callback_data=f"calendar:info")])

        keyboard = None
        if len(buttons) > 0: keyboard = InlineKeyboardMarkup(buttons)

        message.reply('Доступные подписки:', reply_markup=keyboard)

    if message.text == '👤 Мои подписки':
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

    if message.text == '💬 Отзывы участников клуба':
        message.reply('https://t.me/donclub_feedback')

    if message.text == '📢 Реф. Программа':
        count = db.get_count_refs(message.chat.id)[0]['COUNT(*)']

        message.reply(
            f'''
Ваш баланс: <b>{round(db.get_balance(message.chat.id), 2)}$</b>

Вы привлекли <b>{count} рефералов</b>
Ваша ссылка:
https://t.me/{bot.get_me().username}?start=ref-{message.chat.id}

Приводи по своей реферальной ссылке людей и получай {config.ref_procent}% с их покупок себе на баланс!
            ''',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [ 
                    [InlineKeyboardButton('💸 Заказать вывод', callback_data='output')]
                ]
            )
        )

    if message.chat.id in admin_id:
        if 'admin' in message.text.lower():
            message.reply('<b>Админ-Панель</b>', reply_markup=ADMIN)
            db.set_status(message.chat.id, 'admin')

        if message.text == '⬆️ Экспорт данных':
            message.reply('Для выгрузки данных нажмите - /ExportData')

        if '/ExportData' in message.text:
            message.reply('Подождите...')
            path = db.export_data_to_xlsx(bot.get_users)
            message.reply_document(path)
            db.os.remove(path)

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

            statistic = db.get_time_statistic()

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
<b>Информация о товаре</b>:

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

        if '/onProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_product_work(product_id, 1)
            message.reply('Готово!')

        if '/offProduct_' in message.text:
            product_id = int(message.text.split('_')[1])
            db.set_product_work(product_id, 0)
            message.reply('Готово!')
        
        if '/deleteProduct' in message.text:
            product_id = int(message.text.split('_')[1])
            db.del_product(product_id)
            message.reply('Готово!')
        
        if '/editSub_' in message.text:
            sub_id = int(message.text.split('_')[1])
            sub = db.get_sub(sub_id)

            if sub['work'] == 1: work = 'работает'
            else: work = 'выключен'

            message.reply(
                f'''
<b>Информация о подписке</b>:

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

        if '/offSub_' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.set_sub_work(sub_id, 0)
            message.reply('Готово!')
        
        if '/deleteSub' in message.text:
            sub_id = int(message.text.split('_')[1])
            db.del_sub(sub_id)
            message.reply('Готово!')
    
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
<b>Информация о промокоде:</b>

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

        if '/offPromocode_' in message.text:
            db.set_pc_work(int(message.text.split('_')[1]), 0)
            message.reply('Готово!')

        if '/offPromocode_' in message.text:
            pass
        
        if '/deletePromocode_' in message.text:
            pc_id = int(message.text.split('_')[1])
            db.del_promocode(pc_id)
            message.reply('Готово!')

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
                            InlineKeyboardButton('Binance (внутренний платеж)', callback_data=f'calendarForm:internal'),
                            InlineKeyboardButton('Другое (внешний платеж)', callback_data=f'calendarForm:external')
                        ]
                    ]
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
                f"Платежи принимаются только в <b>USDT</b>. Пожалуйста, выберите с какого кошелька вы собираетесь провести оплату {sub['price']}$:", 
                reply_markup=InlineKeyboardMarkup(
                    [ 
                        [
                            InlineKeyboardButton('Binance (внутренний платеж)', callback_data=f'payment_form:pc:{sub_id}:internal'),
                            InlineKeyboardButton('Другое (внешний платеж)', callback_data=f'payment_form:pc:{sub_id}:external')
                        ],
                        [InlineKeyboardButton('⬅️ Назад', callback_data=f"product:{sub['product_id']}")]
                    ]
                )
            )

        if form == 'pc':
            transfer_type = call.data.split(':')[3]
            call.message.delete()
            call.message.reply(
                'Введите промокод на скидку если он у вас есть:', 
                reply_markup=ReplyKeyboardMarkup(
                    [ 
                        [KeyboardButton('➡️ Пропустить')],
                        [KeyboardButton('⬅️ Назад')]
                    ], True, False
                )
            )
            db.set_status(call.message.chat.id, f'sendPromocode:{sub_id}:{transfer_type}')

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
            call.message.edit_text('<b>txid</b> подтвержден!')
            channels = db.get_product_channels(sub['product_id'])
            links = [(acc.bot.create_chat_invite_link(channel, member_limit=1).invite_link, bot.get_chat(channel).type) for channel in channels]

            bot.send_message(
                user_id,
                'Ваш txid успешно прошёл проверку ✅\n\nПереходите к нам в клуб по ссылкам ниже', 
                reply_markup=InlineKeyboardMarkup(
                    [ 
                        [InlineKeyboardButton('Канал' if chat_type == 'channel' else 'Чат', url=link)] for link, chat_type in links
                    ]
                )
            )

            for link in links:
                db.add_link(link[0], db.get_product(sub['product_id'])['channel_id'], user_id)

            '''sub = db.get_subscriber_sub(user_id, sub_id)
            if sub == None: db.add_subscriber(user_id, sub_id)
            else: db.set_subscriber_finish_date(user_id, sub_id, db.get_timestamp(str(db.get_strptime(str(db.get_date_from_timestamp(sub['finish_date']))) + db.timedelta(days=db.get_sub(sub['sub_id'])['period']))))'''

            subscribe = db.get_sub_on_product_id(call.message.chat.id, sub['product_id'])
            if subscribe == None: db.add_subscriber(user_id, sub_id)
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

def scheduler():
    def check_links():
        for link in db.get_links():
            if type(link['chat_id']) in [str]: db.del_link(link['link']); return

            users = acc.get_chat_invite_link_members(chat_id=link['chat_id'], invit_link=link['link'])
            if len(users) > 0:
                if users[0].user.id == link['target_user_id']:
                    db.del_link(link['link'])
                else:
                    db.del_link(link['link'])
                    acc.bot.kick_chat_member(link['chat_id'], users[0].user.id)
                    acc.bot.unban_chat_member(link['chat_id'], users[0].user.id)

    def check_subscribers():
        users = db.get_subscribers()

        for user in users:
            if user['finish_date'] != 0:
                if user['finish_date'] <= db.get_timestamp(db.get_date_now()):
                    for channel_id in db.get_product_channels(db.get_sub(user['sub_id'])['product_id']):
                        try: bot.ban_chat_member(channel_id, user['user_id'])
                        except Exception as e: bot.send_message(735904174, f"Пользователь не удален, причина - {e}\nt.me/{bot.get_users(user['user_id']).username} ({user['user_id']})")
                        try: bot.unban_chat_member(channel_id, user['user_id'])
                        except Exception as e: bot.send_message(735904174, f"Пользователь не удален, причина - {e}\nt.me/{bot.get_users(user['user_id']).username} ({user['user_id']})")

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
                    except:
                        pass
                
                else:
                    days_laft = (db.get_strptime(db.get_date_now()) - db.get_strptime(db.get_date_from_timestamp(user['finish_date']))).days

                    if days_laft == -2:
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
                        
                        except: pass
                    
                    if days_laft == -1:
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
                        
                        except: pass

    schedule.every().day.at("00:00").do(check_subscribers)
    #schedule.every(2).minutes.do(check_subscribers)
    schedule.every(1).minutes.do(check_links)

    while True:
        try:
            schedule.run_pending()
        
        except:
            text = format_exc()
            if len(text) > 4096:
                for x in range(0, len(text), 4096):
                    bot.send_message(735904174, text[x:x+4096])
            else: bot.send_message(735904174, text)

            schedule.clear()
            scheduler()
        sleep(1)        


Thread(target=scheduler).start()
bot.run()
