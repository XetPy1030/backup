from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice, reversed_buttons
import asyncio
from aiogram import filters, types


@dp.message_handler(db_status=[db, 'order_cont_1'])
async def process_nofyte(message: types.Message):
    txt = message.text.replace(" ", "")
    try:
        if "-" in txt:
            spl = txt.split("-")
            spl = map(int, spl)
            start, end = spl
        else:
            start = end = int(txt)
        db.set_status(message.chat.id, f"order_cont_2:{start}:{end}")
        await message.answer(lang["order_stickers_2"], reply_markup=markups.cont_f_u_1)
    except Exception:
        await message.answer("Неправильный формат, попробуйте снова")


@dp.message_handler(db_status=[db, 'ad_psts'])
async def process_notegyf(message: types.Message):
    chat = message.text
    userid = message.chat.id

    await bot.send_message(int(config["Links"]["send_orders"]),
      lang["ad_psts_send_msg"].format(
        id=f'<a href="tg://user?id={userid}">{userid}</a>',
        desc=chat,
        username="@" + message.chat.username if message.chat.username else "Без username"
      ),
      reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
    )

    db.set_status(message.chat.id)
    await message.answer(lang["ord_ad_psts"], reply_markup=button_menu_choice(message.chat.id))


@dp.message_handler(db_status=[db, 'order_cont_2'])
async def process_notegyf(message: types.Message):
    chat = message.text
    userid = message.chat.id
    txt = db.get_status(userid).split(":")[1]

    await bot.send_message(int(config["Links"]["send_orders"]),
      lang["cont_send"].format(
        id=f'<a href="tg://user?id={userid}">{userid}</a>',
        num=f"{txt}",
        desc=chat,
        username="@" + message.chat.username if message.chat.username else "Без username"
      ),
      reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
    )
    
    db.set_status(message.chat.id)
    await message.answer(lang["order_stickers_send"], reply_markup=button_menu_choice(message.chat.id))


@dp.message_handler(db_status=[db, 'sticks_order'])
async def process_note(message: types.Message):
    chat = message.text
    userid = message.chat.id
    types = {"anim": lang["anim_stickers"], "stat": lang["stat_stickers"]}
    type_st = types[db.get_status(userid).split(":")[1]]

    await bot.send_message(int(config["Links"]["send_orders"]),
      lang["stickers_send_msg"].format(
        id=f'<a href="tg://user?id={userid}">{userid}</a>',
        type=type_st,
        desc=chat,
        username="@" + message.chat.username if message.chat.username else "Без username"
      ),
      reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
    )
    
    db.set_status(message.chat.id)
    await message.answer(lang["order_stickers_send"], reply_markup=button_menu_choice(message.chat.id))


@dp.message_handler(db_status=[db, 'chan_des_order'])
async def process_note(message: types.Message):
    chat = message.text
    userid = message.chat.id
    types = {"anim": lang["anim_stickers"], "stat": lang["stat_stickers"]}
    type_st = types[db.get_status(userid).split(":")[1]]

    await bot.send_message(int(config["Links"]["send_orders"]),
      lang["chan_des_send_msg"].format(
        id=f'<a href="tg://user?id={userid}">{userid}</a>',
        type=type_st,
        desc=chat,
        username="@" + message.chat.username if message.chat.username else "Без username"
      ),
      reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
    )
    
    db.set_status(message.chat.id)
    await message.answer(lang["order_stickers_send"], reply_markup=button_menu_choice(message.chat.id))
