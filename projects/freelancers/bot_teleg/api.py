import requests
import json
import config

headers = {
  'x-api-key': config.api_for_nowpayments,
  'Content-Type': 'application/json'
}

def get_currencies():
    url = "https://api.nowpayments.io/v1/currencies"
    response = requests.request("GET", url, headers=headers, data={})
    return response.json()

def get_payment(id):
    url = f"https://api.nowpayments.io/v1/payment/{id}"
    response = requests.request("GET", url, headers=headers, data={})
    return response.json()

def get_price(amount, currency, to):
    url = f"https://api.nowpayments.io/v1/estimate?amount={amount}&currency_from={currency}&currency_to={to}"
    response = requests.request("GET", url, headers=headers, data={})
    return response.json()

def create_payment(amount, currency, description, return_url):
    pay = get_price(amount, "USD", currency)['estimated_amount']
    payload = json.dumps({
        "pay_amount": pay,
        "pay_currency": currency,
        "price_amount": amount,
        "price_currency": "usd",
        "ipn_callback_url": return_url,
        "order_id": "RGDBP-21314",
        "order_description": description
    })
    url = "https://api.nowpayments.io/v1/payment"
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

#---------------------
# получить список валют:
# get_currencies()
"""
возвращает:

{'currencies': [...]}                 # <---- массив валют
"""
#---------------------
# создать платеж:
# create_payment(
#   680,                              # <---- сумма в валюте платежа
#   "btc",                            # <---- валюта платежа
#   "test",                           # <---- описание платежа
#   "https://example.com"             # <---- адрес для обратной связи
# )
"""
возвращает:

{
    'payment_id': '5049336150',       # <---- идентификатор платежа
    'payment_status': 'waiting',
    'pay_address': '38St8D2xJdKwWGSWH4ySgiM8ay9NjchV53',
    ...
}
"""
#---------------------
# получить статус платежа:
# get_payment(
#   "5049336150"                      # <---- идентификатор платежа
# )
"""
возвращает:

{
    'payment_id': 5049336150, 
    'invoice_id': None, 
    'payment_status': 'waiting',      # <---- статус платежа
    'pay_address': '38St8D2xJdKwWGSWH4ySgiM8ay9NjchV53'
    ...
}
"""
#---------------------
# получить цену платежа:
# get_price(
#   680,                              # <---- сумма в валюте платежа
#   "usd"                             # <---- валюта возврата
#   "btc",                            # <---- валюта платежа
# )
"""
возвращает:

{
    'currency_from': 'usd', 
    'amount_from': 680, 
    'currency_to': 'btc',
    'estimated_amount': '0.03179213'  # <---- сумма в валюте возврата
}
"""
#---------------------

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime as dt
import json
import random

def create_plot(data):
    fmt = dates.DateFormatter('%m.%d %H:%M')

    prices = []
    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    time_interval = [dt.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in data['dates']]
    y = np.array([x for x in range(len(prices))])
    x = np.array([x for x in range(len(prices))])

    ax.plot(time_interval, data['prices'], "-o")
    name = f"plot{random.randint(0, 10000)}.png"
    ax.set_title("График зависимости заработка от времени")
    plt.savefig(name)

    return name


#data = {
#    "dates": ['2020-01-01 00:00:00', '2020-02-01 00:00:00', '2020-03-01 00:00:00'],
#    "prices": [136, 12543, 11346677]
#}
#create_plot(data)