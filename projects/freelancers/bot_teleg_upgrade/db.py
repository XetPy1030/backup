import sqlite3
import config
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar, requests, json, pandas

from random import randint, random
from time import sleep

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_date_now(t='%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(t)

def get_date_from_timestamp(timestamp, t='%Y-%m-%d %H:%M:%S'):
    return datetime.fromtimestamp(timestamp).strftime(t)

def get_timestamp(date, t='%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(date, t).timestamp()

def get_next_date(year=None, month=None, days=None, hours=None, minutes=None, seconds=None, t='%Y-%m-%d %H:%M:%S'):
    now = datetime.now()

    if year != None: next_date = now + relativedelta(years=1)
    if month != None: next_date = now + timedelta(days=calendar.monthrange(date.today().year, date.today().month)[1])
    if days != None: next_date = now + timedelta(days=days)
    if hours != None: next_date = now + timedelta(hours=hours)
    if minutes != None: next_date = now + timedelta(minutes=minutes)
    if seconds != None: next_date = now + timedelta(seconds=seconds)

    return next_date.strftime(t)

def get_strptime(date, t='%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(date, t)

def export_data_to_xlsx(get_user_func):
    '''выгрузка платежей'''
    path = f'downloads/{create_unique_id()}_table.xlsx'
    writer = pandas.ExcelWriter(path, engine='xlsxwriter')

    user_id, username, amount, date = [], [], [], []
    sheet_name = 'payments'

    for payment in get_all_payments_history():
        user_id.append(payment['user_id'])
        username.append(f"https://t.me/{get_user_func(payment['user_id']).username}")
        amount.append(payment['amount'])
        date.append(get_date_from_timestamp(payment['date']))

    pandas.DataFrame({'user_id': user_id, 'username': username, 'amount': amount, 'date': date}).to_excel(writer, sheet_name=sheet_name)

    '''выгрузка подписчиков'''
    user_id, username, sub_id, date = [], [], [], []
    sheet_name = 'subscribers'

    for sub in get_subscribers(type='all'):
        user_id.append(sub['user_id'])
        username.append(f"https://t.me/{get_user_func(sub['user_id']).username}")
        sub_id.append(sub['sub_id'])
        date.append(get_date_from_timestamp(sub['finish_date']))

    pandas.DataFrame({'user_id': user_id, 'username': username, 'sub_id': sub_id, 'date': date}).to_excel(writer, sheet_name=sheet_name)

    writer.save()
    return path

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_conection(data='data.db'): 
    conn = sqlite3.connect(data)
    conn.row_factory = dict_factory
    return conn

def add_user(user_id):
    conn = get_conection()
    cursor = conn.cursor()

    data = (
        user_id, 
        None,
        0,
        0
    )

    cursor.execute("INSERT INTO users VALUES (?,?,?,?)", data)
    conn.commit()
    conn.close()

def set_balance(user_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE users 
SET balance = ?
WHERE id = ?
"""
    cursor.execute(sql, (data, user_id))
    conn.commit()
    conn.close()

def set_status(user_id, new_status=None):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE users 
SET status = ?
WHERE id = ?
"""
    cursor.execute(sql, (new_status, user_id))
    conn.commit()
    conn.close()

def get_status(user_id):
    return get_user(user_id)['status']

def get_balance(user_id):
    return get_user(user_id)['balance']

def get_users():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM users").fetchall()
    conn.close()
    return data

def mailing():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM users WHERE del = ?", (0,)).fetchall()
    conn.close()
    return data

def set_delete(user_id, delete):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE users 
SET del = ?
WHERE id = ?
"""
    cursor.execute(sql, (delete, user_id))
    conn.commit()
    conn.close()

def get_subscribers(type=config.subscribers_type['product']):
    conn = get_conection()
    cursor = conn.cursor()
    if type == 'all': data = cursor.execute("SELECT * FROM subscribers").fetchall()
    else: data = cursor.execute("SELECT * FROM subscribers WHERE type = ?", (type,)).fetchall()
    conn.close()
    return data

def get_subscribers_count_for_product(product_id):
    count = 0
    for subscriber in get_subscribers():
        sub = get_sub(subscriber['sub_id'])
        if sub != None and sub['product_id'] == product_id:
            count += 1

    return count

def get_user(user_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = data.fetchone()
    conn.close()
    return user

def create_unique_id():
    return randint(1, 10000000000)

def get_user_referer(user_id):
    conn = get_conection()
    cursor = conn.cursor()
    referer = cursor.execute(f"SELECT * from referals where referal = ?", (user_id,)).fetchone()
    conn.close()
    return referer['referer'] if referer != None else None

def add_new_referal(referer_id, referal_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = (
        referer_id, 
        referal_id
    )
    cursor.execute("INSERT INTO referals VALUES (?,?)", data)
    conn.commit()
    conn.close()

def get_count_refs(user_id):
    conn = get_conection()
    cursor = conn.cursor()
    count = cursor.execute(f"SELECT COUNT(*) from referals where referer = ?", (user_id,)).fetchall()
    conn.close()
    return count

def delete(id_):
    conn = get_conection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM turn WHERE id = ?", (id_,))
    conn.commit()
    conn.close()

def add_product(channel_id):
    conn = get_conection()
    cursor = conn.cursor()
    product_id = create_unique_id()
    data = (
        product_id, 
        json.dumps({'channels': [channel_id]}),
        None,
        None,
        0
    )
    cursor.execute("INSERT INTO products VALUES (?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    return product_id

def get_product_channels(product_id):
    return json.loads(get_product(product_id)['channel_id'])['channels']

def get_product(product_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    conn.close()
    return data 

def get_products_work():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM products WHERE work = 1").fetchall()
    conn.close()
    return data

def get_products_all():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM products").fetchall()
    conn.close()
    return data

def del_product(product_id):
    conn = get_conection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    cursor.execute('DELETE FROM subs WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()

def set_product_name(product_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE products 
SET name = ?
WHERE product_id = ?
"""
    cursor.execute(sql, (data, product_id))
    conn.commit()
    conn.close()

def set_product_about(product_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE products 
SET about = ?
WHERE product_id = ?
"""
    cursor.execute(sql, (data, product_id))
    conn.commit()
    conn.close()

def set_product_work(product_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE products 
SET work = ?
WHERE product_id = ?
"""
    cursor.execute(sql, (data, product_id))
    conn.commit()
    conn.close()

def add_channel_in_product(product_id, data):
    channels = get_product_channels(product_id)
    channels.append(data)
    channels = json.dumps({'channels': channels})

    conn = get_conection()
    cursor = conn.cursor()
    sql = f"""
UPDATE products 
SET channel_id = ?
WHERE product_id = ?
"""
    cursor.execute(sql, (channels, product_id))
    conn.commit()
    conn.close()


def del_channel_from_product(product_id, data):
    channels = get_product_channels(product_id)
    channels.remove(data)
    channels = json.dumps({'channels': channels})
    
    conn = get_conection()
    cursor = conn.cursor()
    sql = f"""
UPDATE products 
SET channel_id = ?
WHERE product_id = ?
"""
    cursor.execute(sql, (channels, product_id))
    conn.commit()
    conn.close()

def add_sub(product_id):
    conn = get_conection()
    cursor = conn.cursor()
    sub_id = create_unique_id()
    data = (
        sub_id,
        product_id,
        None, 
        None,
        None,
        0
    )
    cursor.execute("INSERT INTO subs VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    return sub_id

def get_sub(sub_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subs WHERE sub_id = ?", (sub_id,)).fetchone()
    conn.close()
    return data 

def get_product_subs(product_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subs WHERE product_id = ?", (product_id,)).fetchall()
    conn.close()
    return data

def get_product_subs_work(product_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subs WHERE product_id = ? AND work = 1", (product_id,)).fetchall()
    conn.close()
    return data

def del_sub(sub_id):
    conn = get_conection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subs WHERE sub_id = ?', (sub_id,))
    conn.commit()
    conn.close()

def set_sub_name(sub_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE subs 
SET name = ?
WHERE sub_id = ?
"""
    cursor.execute(sql, (data, sub_id))
    conn.commit()
    conn.close()

def set_sub_period(sub_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE subs 
SET period = ?
WHERE sub_id = ?
"""
    cursor.execute(sql, (data, sub_id))
    conn.commit()
    conn.close()

def set_sub_price(sub_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE subs 
SET price = ?
WHERE sub_id = ?
"""
    cursor.execute(sql, (data, sub_id))
    conn.commit()
    conn.close()

def set_sub_work(sub_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE subs 
SET work = ?
WHERE sub_id = ?
"""
    cursor.execute(sql, (data, sub_id))
    conn.commit()
    conn.close()

def add_subscriber(user_id, sub_id, finish_date=None, type=config.subscribers_type['product']):
    if finish_date == None: finish_date = get_timestamp(get_next_date(days=get_sub(sub_id)['period']))
    conn = get_conection()
    cursor = conn.cursor()
    data = (
        user_id,
        sub_id,
        finish_date,
        type
    )
    cursor.execute("INSERT INTO subscribers VALUES (?,?,?,?)", data)
    conn.commit()
    conn.close()

def set_subscriber_finish_date(user_id, sub_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE subscribers 
SET finish_date = ?
WHERE user_id = ?
AND sub_id = ?
"""
    cursor.execute(sql, (data, user_id, sub_id))
    conn.commit()
    conn.close()

def get_subscriber(user_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subscribers WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return data

def get_subscriber_sub(user_id, sub_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subscribers WHERE user_id = ? AND sub_id = ?", (user_id,  sub_id)).fetchone()
    return data

def get_sub_on_product_id(user_id, product_id):
    '''вернет действующую подписку на определенный продукт '''
    for subscribe in get_subscriber(user_id):
        sub = get_sub(subscribe['sub_id'])
        if sub != None and sub['product_id'] == product_id:
            return subscribe

def get_calendar_subscribers():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subscribers WHERE type = ?", (config.subscribers_type['calendar'],)).fetchall()
    conn.close()
    return data

def check_user_calendar(user_id):
    '''Вернет True если у пользователя есть подписка на календарь'''
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM subscribers WHERE type = ? AND user_id = ?", (config.subscribers_type['calendar']), user_id).fetchone()
    conn.close()
    return True if data != None else False

def del_subscriber(user_id, sub_id):
    conn = get_conection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscribers WHERE user_id = ? AND sub_id = ?", (user_id, sub_id))
    conn.commit()
    conn.close()

def add_promocode(data):
    conn = get_conection()
    cursor = conn.cursor()
    pc_id = create_unique_id()
    data = (
        pc_id,
        data,
        0,
        0,
        0,
        0
    )
    cursor.execute("INSERT INTO promocodes VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    return pc_id

def get_promocode(promocode_id=None, data=None):
    conn = get_conection()
    cursor = conn.cursor()
    if promocode_id != None: pc = cursor.execute("SELECT * FROM promocodes WHERE promocode_id = ?", (promocode_id,)).fetchone()
    if data != None: pc = cursor.execute("SELECT * FROM promocodes WHERE data = ?", (data,)).fetchone()
    conn.close()
    return pc

def get_promocodes():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM promocodes").fetchall()
    conn.close()
    return data

def set_pc_total_count_uses(promocode_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE promocodes 
SET total_count_uses = ?
WHERE promocode_id = ?
"""
    cursor.execute(sql, (data, promocode_id))
    conn.commit()
    conn.close()

def set_pc_count_uses(promocode_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE promocodes 
SET count_uses = ?
WHERE promocode_id = ?
"""
    cursor.execute(sql, (data, promocode_id))
    conn.commit()
    conn.close()

def set_pc_discount(promocode_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE promocodes 
SET discount = ?
WHERE promocode_id = ?
"""
    cursor.execute(sql, (data, promocode_id))
    conn.commit()
    conn.close()

def set_pc_work(promocode_id, data):
    conn = get_conection()
    cursor = conn.cursor()

    sql = f"""
UPDATE promocodes 
SET work = ?
WHERE promocode_id = ?
"""
    cursor.execute(sql, (data, promocode_id))
    conn.commit()
    conn.close()

def del_promocode(promocode_id):
    conn = get_conection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promocodes WHERE promocode_id = ?", (promocode_id,))
    conn.commit()
    conn.close()

def add_payment_in_history(user_id, summ, date):
    conn = get_conection()
    cursor = conn.cursor()

    data = (
        user_id,
        summ,
        date
    )

    cursor.execute("INSERT INTO payments_history VALUES (?,?,?)", data)
    conn.commit()
    conn.close()

def get_payments_history(user_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM payments_history WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return data

def get_all_payments_history():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM payments_history").fetchall()
    conn.close()
    return data

def get_all_payments_history():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM payments_history").fetchall()
    conn.close()
    return data

def get_time_statistic():
    statistic = {
        'day': 0,
        'month': 0,
        'total': 0
    }

    payments = get_all_payments_history()
    for payment in payments:
        operation_date = get_date_from_timestamp(payment['date'])
        operation_date = get_strptime(operation_date)

        today = get_strptime(get_date_now())
        today = datetime(today.year, today.month, today.day, 0, 0, 0)

        tomorrow = get_strptime(get_next_date(days=1))
        tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)

        first_day_of_month = get_strptime(get_date_now())
        first_day_of_month = datetime(first_day_of_month.year, first_day_of_month.month, 1, 0, 0, 0)

        last_day_of_month = get_strptime(get_next_date(month=1))
        last_day_of_month = datetime(last_day_of_month.year, last_day_of_month.month, 1, 0, 0, 0)

        if today <= operation_date < tomorrow: 
            statistic['day'] += payment['amount']

        if first_day_of_month <= operation_date < last_day_of_month: 
            statistic['month'] += payment['amount']
        
        statistic['total'] += payment['amount']

    return statistic

def get_user_payments(user_id):
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM payments_history WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return data

def get_count_purchased_users():
    count = 0
    for user in get_users():
        if len(get_user_payments(user['id'])) > 0: count += 1
    return count

def get_purchased_users():
    users = []
    for user in get_users():
        if len(get_user_payments(user['id'])) > 0 : users.append(user)
    return users

def get_not_purchased_users():
    users = []
    for user in get_users():
        if len(get_user_payments(user['id'])) == 0: users.append(user)
    return users

def check_email_valid(email):
    return requests.get(f"https://api.2ip.me/email.txt?email={email}").json()

def add_link(link, chat_id, target):
    conn = get_conection()
    cursor = conn.cursor()

    data = (
        link, 
        chat_id,
        target
    )

    cursor.execute("INSERT INTO links VALUES (?,?,?)", data)
    conn.commit()
    conn.close()

def get_links():
    conn = get_conection()
    cursor = conn.cursor()
    data = cursor.execute("SELECT * FROM links").fetchall()
    conn.close()
    return data

def del_link(link):
    conn = get_conection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM links WHERE link = ?", (link,))
    conn.commit()
    conn.close()

def _start_sql_command(filename):
    conn = get_conection()
    cursor = conn.cursor()

    with open(filename) as lines:
        for command in lines.readlines():
            cursor.execute(command)

    conn.commit()
    conn.close()