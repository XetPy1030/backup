token = '5576822686:AAEE-AhQm9zlWetDsN3xPYOw6XuLHjj-0Ck'

admin_ids = []
send_feedback = -740606993 # кто чекает обратную связь
check_pay = -740606993

link_feedback_from_club_members = 'https://t.me/donclub_feedback'

subscribers_type = {
    'product': 1,
    'calendar': 2
}

ref_procent = 20

buttons = {
    'shop': '🛍 Магазин',
    'my_subscription': '👤 Мои подписки',
    'feedback_from_club_members': '💬 Отзывы участников клуба',
    'referall_program': '📢 Реф. Программа',
    'feedback': 'Обратная связь',
    'export_data': '⬆️ Экспорт данных',
    'mailing': '📮 Рассылка',
    'statistics': '📊 Статистика',
    'add_product': '➕ Добавить продукт',
    'edit_product': '⚙️ Настроить продукт',
    'add_promocode': '➕ Добавить промокод',
    'edit_promocode': '⚙️ Настроить промокод',
    'back': '⬅️ Назад',
    'admin': 'Админ-Панель',
    'order_withdrawal': '💸 Заказать вывод',
}

markups = {
    'menu': [
        ['shop', 'my_subscription'],
        ['feedback_from_club_members'],
        ['referall_program'],
        ['feedback']
    ],
    'admin': [
        ['export_data'],
        ['mailing', 'statistics'],
        ['add_product', 'edit_product'],
        ['add_promocode', 'edit_promocode'],
        ['back']
    ],
    'back': [
        ['back']
    ]
}


def get_markups(fun, markups_list: list):
    global buttons
    markups_after_fun = []
    for i in markups_list:
        line = []
        for o in i:
            line.append(fun(buttons[o]))
        markups_after_fun.append(line)
    return markups_after_fun
