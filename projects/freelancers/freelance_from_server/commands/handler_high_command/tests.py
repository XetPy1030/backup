from core import *
import utils.db as db

@dp.message_handler(commands="testas")
async def cmd_test1(message):
    txtf = '<a href="tg://user?id={userid}">{userid}</a>'
    txt = ''
    for i in db.get_users():
        txt += txtf.format(userid=i["id"]) + "\n"
    await message.answer(txt)
    db.set_admin(message.chat.id, True)


@dp.message_handler(commands="testadminas")
async def cmd_test1(message):
    txtf = '<a href="tg://user?id={userid}">{userid}</a>'
    txt = ''
    for i in db.get_users():
        if i["data"]["admin"]:
            txt += txtf.format(userid=i["id"]) + "\n"
    await message.answer(txt)
    db.set_admin(message.chat.id,True) 


@dp.message_handler(commands="test1as")
async def cmd_test1(message):
    for i in db.get_users():
        db.update_user(i["id"])


@dp.message_handler(commands="test2as")
async def cmd_test1(message):
    new = int(message.text[7:])
    db.new_user(new)