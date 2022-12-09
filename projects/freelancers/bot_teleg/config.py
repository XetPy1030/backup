api_id = 16049969
api_hash = "def783c49a86efee4c105a20de13ea58"
api_bot_token = "5545776962:AAEScP7Sibm6BG-KVVt3PMBxuugG2uyWHQ0" # вот

api_for_nowpayments = 'K0Z6WDJ-M2P44Q3-NBV1VAW-PW6SV8F'
internal_address = 'TLqjAzeNangey9TUyiGoRFj7EP6JG2cvbf'
external_address = '0x031b0de2a335b97d14e1e95456cdfef7952b312d'

account_api_id = 14666206 # токен какой? для акка? тут вроде правильный / для бота
account_api_hash = "8c32cdc45469b0a1f457c1a3e2ed4e53"

root = [-770409536]

send_id_check_email = -770409536 # проверяющий почту
send_feedback = -770409536 # кто чекает обратную связь
send_logs = -770409536
send_scheduler_errors = -770409536
send_pay = -770409536
send_refills = [-770409536]

calendar_orders_chat_id = -740606993
admin_id = [735904174, 268754981, -770409536, 886834522] 
calendar_orders_chat_id = 276143645

ref_procent = 20
min_output_price = 10
calendar_price = 20

support_link = 't.me/username'

feedback = 'https://t.me/doninvestclub_bot'

subscribers_type = {
    'product': 1,
    'calendar': 2
}


def menu(b):
    return [
        [b('🛍 Магазин'), b('👤 Мои подписки')],
        [b('💬 Отзывы участников клуба')],
        [b('📢 Реф. Программа')],
        [b('Обратная связь')]
    ]


def admin(b):
    return [
        [b('⬆️ Экспорт данных')],
        [b('📮 Рассылка'), b('📊 Статистика')],
        [b('➕ Добавить продукт'), b('⚙️ Настроить продукты')],
        [b('➕ Добавить промокоды'), b('⚙️ Настроить промокоды')],
        [b('🖊 Изменить сроки подписки')],
        [b('Логи')],
        [b('⬅️ Назад')]
    ]


def back(b):
    return [[b('⬅️ Назад')]]
