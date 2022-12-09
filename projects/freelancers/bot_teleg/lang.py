referral_program = '''
Ваш баланс: <b>{balance}$</b>

Вы привлекли <b>{count} рефералов</b>
Ваша ссылка:
https://t.me/{username}?start=ref-{chat_id}

Приводи по своей реферальной ссылке людей и получай {ref_procent}% с их покупок себе на баланс!''' # noqa

feedback_check = 'Вам пришло смс обратной связи!\n@{username} [<a href="tg://user?id={id}">account</a>:{id}]: {message}'

feedback_text = 'Напишите следующим сообщением что передать:' # noqa
after_feedback = 'Спасибо! Мы ответим вам в ближайшее время.'

email_error = 'Отправьте почту в формате username@gmail.com\n\nПринимаются только Google e-mail'

email_for_check = '<b>Почта для проверки!</b>\nАдрес: <code>{email}</code>'

email_sended = '<b>Почта отправлена!</b> Мы сообщим когда она будет добавлена'

debug_change = '@{username}:[id:{id}]:{action}:{old}:{new}'
debug = '@{username}:[id:{id}]:{action}:{new}'
