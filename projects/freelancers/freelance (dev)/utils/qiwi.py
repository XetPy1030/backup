import requests
from uuid import uuid4
from aiogram import types
from config import config


def generate_check_markups():
    payment_id = str(uuid4())
    inline_buy_train = types.InlineKeyboardMarkup()
    inline_buy_train.add(types.InlineKeyboardButton(
        "Купить",
        callback_data=f"services:train_check:{payment_id}"
        )
    )
    return [payment_id, inline_buy_train]


def payment_history_last(my_login, api_access_token, rows_num=1):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': rows_num}
    print("req")
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    print('resp')
    return h.json()

def check_payment(pay_id) -> bool:
    pays = payment_history_last(
        config["Login"]["number"],
        config["Login"]["token_qiwi"],
        )
    
    for pay in pays["data"]:
        if pay['error'] is None and\
        pay['status'] == 'SUCCESS' and\
        pay['total']['amount'] >= int(config['Login']['cost_train']) and\
        pay_id in pay['comment']:
            return True
    
    return False
