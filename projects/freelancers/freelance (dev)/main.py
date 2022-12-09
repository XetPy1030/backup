import configparser
import logging

from aiogram import executor, types

import utils.db as db
import utils.markups as markups
import utils.my_filters as my_filters
from core import bot, dp

config = configparser.ConfigParser()
config.read("config.ini")

buttons = config['Buttons']
lang = config['Language']

reversed_buttons = {}
for i in dict(buttons).keys():
    reversed_buttons[buttons[i]] = i

reversed_lang = {}
for i in dict(lang).keys():
    reversed_lang[lang[i]] = i

# print(config["Twitter"]["username"])
# print(config['Login']['token'])
# наши услуги, отзывы, обратная связь, наши партнеры

#bot = Bot(token=config['Login']['token'])
#storage = MemoryStorage()
#dp = Dispatcher(bot, storage=storage)
#bot.parse_mode = "HTML"
logging.basicConfig(level=logging.INFO)


dp.filters_factory.bind(my_filters.StatusCheck, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(my_filters.IdCheck, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(my_filters.AdminCheck, event_handlers=[dp.message_handlers])
dp.filters_factory.bind(my_filters.InlineFilter, event_handlers=[dp.callback_query_handlers])


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "🏠 Главное меню"),
        # types.BotCommand("start", "♻️Перезапуск бота"),
        # types.BotCommand("profile", "Реферальная программа"),
        # types.BotCommand("other_profile", "Другой профиль"),
    ])


def button_menu_choice(id: int):
    return markups.button_menu_with_admin if db.is_admin(id) else markups.button_menu


async def clear_menu(message):
    msg = await message.answer("clear",reply_markup=button_menu_choice(message.chat.id))
    await msg.delete()


import commands


@dp.message_handler(db_status=[db, 'profile'])
async def mailing(message: types.Message):
    try:
        id = message.forward_from.id if message.forward_from else int(message.text)
    except ValueError:
        await message.answer("Число, а не текст")
        return
    db.set_status(message.chat.id)
    user = db.get_user(id)
    from_us = f'<a href="tg://user?id={user["from"]}">{user["from"]}</a>' if user["from"] else "нет"
    await message.answer(f'id: {id}\nПриглашён: {from_us}\nПриглашённых: {len(user["new_users"])}\nСсылка для приглашения: https://t.me/Mango_agency_bot?start=ref-{id}') 


@dp.message_handler(commands="start")
async def cmd_test1(message):
    if not db.is_user(message.chat.id):
        if "ref-" in message.text:
            from_us = int(message.text.split("ref-")[1])
            db.new_user_from_old(message.chat.id, from_us)
        else: db.new_user(message.chat.id)
    db.set_status(message.chat.id, '')
    if False:
        await message.answer_document(open("photos/start.pdf", "rb"), reply_markup=markups.inline_new_start)
        # await message.answer("Выберите", reply_markup=markups.inline_new_start)
        return
    await message.answer_animation(
        open('photos/logov2.gif.mp4', 'rb'),
        caption=lang['hello'],
        reply_markup=button_menu_choice(message.chat.id)
    )

@dp.message_handler(checks=[db, bot])
async def checks(message: types.Message):
    pass


@dp.message_handler(commands="restart")
async def restart(message: types.Message):
    await set_default_commands(dp)
    db.set_status(message.chat.id)
    await message.answer(lang['menu'], reply_markup=button_menu_choice(message.chat.id))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
