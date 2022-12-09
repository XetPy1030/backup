from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config, button_menu_choice
import asyncio
from aiogram import filters, types


@dp.callback_query_handler(status_inline='services')
async def some_inline_handler(inline_query: types.CallbackQuery):
    message = inline_query.message
    userid = message.chat.id
    match inline_query.data.split(':')[1:]:
        case "turnkey_channel", :
            #await clear_menu(message)
            await inline_query.message.answer_photo(
                photo=open('new_photos/channel.png', 'rb'),
                caption=lang['turnkey_channel'],
                reply_markup=markups.inline_turnkey)
        case "turnkey_channel_detail", :
            await inline_query.bot.send_message(
                inline_query.message.chat.id,
                lang['turnkey_channel_detail'],
                reply_markup=markups.inline_turnkey_detail)
        case "ask", :
            await message.answer_photo(open("new_photos/support.png", "rb"), caption=lang['feedback_ans'], reply_markup=markups.button_back, parse_mode='HTML')
            # await inline_query.message.answer(lang['feedback_ans'], reply_markup=markups.button_back)
            db.set_status(inline_query.message.chat.id, 'feedback')
        case "channel_design", :
            await inline_query.message.answer_photo(
                photo=open('new_photos/logo.png', 'rb'),
                caption=lang['logo'],
                reply_markup=markups.inline_logo)
        case "logo_portfolio", :
            mark = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Портфолио", "https://t.me/joinchat/AAAAAFimmzJE4oilskVFxw")
                )
            await inline_query.message.answer('Примеры',
                                              reply_markup=mark,)
        case "channel_promotion", :
            await inline_query.message.answer_photo(
                photo=open('new_photos/up.png', 'rb'),
                caption=lang['channel_promotion'],
                reply_markup=markups.inline_channel_promotion)
        case "channel_promotion_next", :
            await inline_query.message.answer(
                lang['channel_promotion_next'],
                reply_markup=markups.inline_channel_promotion_next,
                disable_web_page_preview=True)
        case "bot_development", :
            await inline_query.message.answer_photo(
                photo=open('new_photos/bot.png', 'rb'),
                caption=lang['bot_development'],
                reply_markup=markups.inline_bot_development)
        case "bot_development_next", :
            await inline_query.message.answer_photo(
                open("photos/price.png", "rb"),
                caption=lang['bot_development_next'],
                reply_markup=markups.inline_bot_development_next
            )
        case "stickers", :
            await inline_query.message.answer_photo(
                photo=open('new_photos/stickers.png', 'rb'),
                caption=lang['stickers'],
                reply_markup=markups.inline_stickers)
        case "stickers_next", :
            stickers = config['Links']['stickers'].split('\n')
            await message.answer(
                lang['stickers_example_1'],
            )
            await message.answer_sticker(stickers[0])
            await message.answer_sticker(stickers[1])
            await asyncio.sleep(3)
            await message.answer(
                lang['stickers_example_2'],
            )
            await message.answer_sticker(stickers[2])
            await message.answer_sticker(stickers[3])
            await asyncio.sleep(3)
            await inline_query.message.answer_photo(
                open("photos/price.png", "rb"),
                caption=lang['stickers_next'],
                reply_markup=markups.inline_stickers_next
            )
        case "advertising_posts", :
            await inline_query.message.answer_photo(
                photo=open('new_photos/ad.png', 'rb'),
                caption=lang['advertising_posts'],
                reply_markup=markups.inline_advertising_posts)
        case "content_for_your_channel", :
            await inline_query.message.answer_photo(
                photo=open('new_photos/content.png', 'rb'),
                caption=lang['content_for_your_channel'],
                reply_markup=markups.inline_content_for_your_channel)
        case "stickers_order", :
            await message.answer(lang["order_stickers_1"], reply_markup=markups.inline_anim_or_stat_stickers)
        case "content_for_your_channel_order", :
            # db.set_status(message.chat.id, "order_cont_1")
            await message.answer(lang["cont_f_u_channel_1"], reply_markup=markups.inline_order_cont_posts)
        case "turnkey_channel_order", :
            await message.answer(lang["chan_pod_key"], reply_markup=button_menu_choice(message.chat.id))
            await bot.send_message(int(config["Links"]["send_orders"]),
              lang["order_null_send"].format(
                id=f'<a href="tg://user?id={userid}">{userid}</a>',
                name="канал под ключ",
                username="@" + message.chat.username if message.chat.username else "Без username"
              ),
              reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
            )
        case "channel_promotion_order", :
            await message.answer(lang["ord_chan_prom"], reply_markup=button_menu_choice(message.chat.id))
            await bot.send_message(int(config["Links"]["send_orders"]),
              lang["order_null_send"].format(
                id=f'<a href="tg://user?id={userid}">{userid}</a>',
                name="продвижение канала",
                username="@" + message.chat.username if message.chat.username else "Без username"
              ),
              reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
            )
        case "bot_development_order", :
            await message.answer(lang["ord_dev_bots"], reply_markup=button_menu_choice(message.chat.id))
            await bot.send_message(int(config["Links"]["send_orders"]),
              lang["order_null_send"].format(
                id=f'<a href="tg://user?id={userid}">{userid}</a>',
                name="разработка ботов",
                username="@" + message.chat.username if message.chat.username else "Без username"
              ),
              reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
            )
        case "logo_order", :
            await message.answer(lang["chan_des_1"], reply_markup=markups.inline_anim_or_stat_chan_des)
        case "advertising_posts_order", :
            db.set_status(userid, "ad_psts")
            await message.answer(lang["ad_p_1"], reply_markup=markups.inline_ad_p)
        case _:
            await inline_query.message.answer('⚙️ Данный разрел находится в разработке')


@dp.callback_query_handler(status_inline='order_cont_posts')
async def ehhehrurhruff(inline_query: types.CallbackQuery):
    txt = inline_query.data.split(":")[1]
    message = inline_query.message
    db.set_status(message.chat.id, f"order_cont_2:{txt}")
    await message.answer(lang["order_stickers_2"], reply_markup=markups.cont_f_u_1)


@dp.callback_query_handler(status_inline='chan_des')
async def ehhehrurhrugy(inline_query: types.CallbackQuery): 
    type = inline_query.data.split(':')[1]
    message = inline_query.message
    db.set_status(message.chat.id, f"chan_des_order:{type}")
    await message.reply(lang["chan_des_2"], reply_markup=markups.chan_des_order_2)


@dp.callback_query_handler(status_inline='chan_order') # cancel
async def hrjurdgcv(inline_query: types.CallbackQuery):
    message = inline_query.message
    chat = "Нет"
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


@dp.callback_query_handler(status_inline='stickers')
async def ehhehrurhru(inline_query: types.CallbackQuery): 
    type = inline_query.data.split(':')[1]
    message = inline_query.message
    db.set_status(message.chat.id, f"sticks_order:{type}")
    await message.reply(lang["order_stickers_2"], reply_markup=markups.stickers_order_2)


@dp.callback_query_handler(status_inline='sticks_order') # cancel
async def dgcv(inline_query: types.CallbackQuery):
    message = inline_query.message
    chat = "Нет"
    userid = message.chat.id
    types1 = {"anim": lang["anim_stickers"], "stat": lang["stat_stickers"]}
    type_st = types1[db.get_status(userid).split(":")[1]]

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


@dp.callback_query_handler(status_inline='ad_psts') # cancel
async def dgcv(inline_query: types.CallbackQuery):
    message = inline_query.message
    chat = "Нет"
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


@dp.callback_query_handler(status_inline='cont_f_u') # cancel
async def dgcv(inline_query: types.CallbackQuery):
    message = inline_query.message
    userid = message.chat.id
    txt = db.get_status(userid).split(":")[1]

    await bot.send_message(int(config["Links"]["send_orders"]),
      lang["cont_send"].format(
        id=f'<a href="tg://user?id={userid}">{userid}</a>',
        num=f"{txt}",
        desc="Пропущено",
        username="@" + message.chat.username if message.chat.username else "Без username"
      ),
      reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(lang["write"], callback_data=f"sendid:{message.chat.id}"))
    )
    
    db.set_status(message.chat.id)
    await message.answer(lang["order_stickers_send"], reply_markup=button_menu_choice(message.chat.id))

