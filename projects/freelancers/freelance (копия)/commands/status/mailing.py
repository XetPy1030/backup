from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice, reversed_buttons
import asyncio
from aiogram import filters, types


@dp.message_handler(db_status=[db, 'mailing'], content_types=types.message.ContentTypes.all())
async def mailing(message: types.Message):
    _, status = db.get_status(message.chat.id).split(':')
    print(status)
    users = []
    change = {'our_services': 'pressed_services',
              'feedbacks': 'pressed_feedbacks',
              'our_partners': 'pressed_partners'}
    match status:
        case "choice":
            status = reversed_buttons[message.text.split(' - ')[1]] if message.text.startswith(lang['button']) else 'all'
            db.set_status(message.chat.id, f'mailing:{status}')
            await message.answer(lang['mailing_choised'], reply_markup=markups.button_back)
            return
        case "all":
            users = db.get_users()
        case "our_services":
            users = db.get_user_with_true_statistics(message.chat.id, change[status])
        case "feedbacks":
            users = db.get_user_with_true_statistics(message.chat.id, change[status])
        case "our_partners":
            users = db.get_user_with_true_statistics(message.chat.id, change[status])

    # users = [{"id": 886834522}]
    nums = 0
    blocked = 0
    for i in users:
        try:
            await bot.forward_message(
                chat_id=i['id'],
                from_chat_id=message.chat.id,
                message_id=message.message_id
                )
            nums += 1
        except Exception as ex:
            blocked += 1 if 'bot was blocked by the user' in str(ex) else 0
            await message.answer(f'Что-то пошло не так.\n{ex}')
    await message.answer(lang['sended'] + f"\nУспешно у {nums} пользователей\nБот заблокирован у {blocked} пользователей", reply_markup=button_menu_choice(message.chat.id))
    db.set_status(message.chat.id)
