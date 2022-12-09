from aiogram import types
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
buttons = config['Buttons']
inline = config['Inline']
lang = config['Language']

button_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_menu_with_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_menu_texts = (
    (
        buttons['our_services'],
        buttons['our_partners']
        ),
    (
        buttons['reviews'],
        buttons['feedbacks']
        )
)
for i in button_menu_texts:
    button_menu.row(*[types.KeyboardButton(o) for o in i])
    button_menu_with_admin.row(*[types.KeyboardButton(o) for o in i])

button_menu_with_admin.add(types.KeyboardButton(buttons['admin']))

button_back = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(buttons['back']))

button_admin = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(buttons['mailing'])).add(types.KeyboardButton(buttons['statistics'])).add(types.KeyboardButton(buttons['back']))

buttons_admin_text = (
    buttons['all'],
    lang['button']+' - '+buttons['our_services'],
    lang['button']+' - '+buttons['our_partners'],
    lang['button']+' - '+buttons['feedbacks'],
    buttons['back']
)
buttons_mailing = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(*[types.KeyboardButton(i) for i in buttons_admin_text])

texts_services = [
    'channel_promotion',
    'bot_development',
    'stickers',
    'turnkey_channel',
    'advertising_posts',
    'channel_design',
    'content_for_your_channel',
    'train',
    'monetization',
]

inline_for_services = types.InlineKeyboardMarkup(row_width=2)
for i in texts_services:
    inline_for_services.add(
        types.InlineKeyboardButton(inline[i], callback_data=f'services:{i}')
        )

inline_turnkey = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
    lang['details'],
    callback_data='services:turnkey_channel_detail'
    ))

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['our_cases'], 'https://t.me/mango_channels'),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:turnkey_channel_order'),
   # types.InlineKeyboardButton(config['Buttons']["back"], callback_data='menu'),
)
inline_turnkey_detail = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_turnkey_detail.insert(i)

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['logo_portfolio'], "https://t.me/joinchat/AAAAAFimmzJE4oilskVFxw"),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:logo_order'),
)
inline_logo = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_logo.insert(i)

inline_channel_promotion = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(lang['next'], callback_data="services:channel_promotion_next")
)

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['portfolio'], "https://t.me/+I5TPjf2ng-szZWZi"),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:channel_promotion_order'),
)
inline_channel_promotion_next = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_channel_promotion_next.insert(i)

inline_bot_development = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(lang['next'], callback_data="services:bot_development_next")
)

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['portfolio'], "https://t.me/portfolio_bots_Mango"),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:bot_development_order'),
)
inline_bot_development_next = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_bot_development_next.insert(i)

inline_stickers = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(lang['next'], callback_data="services:stickers_next")
)

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['portfolio'], "https://t.me/stickerslight"),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:stickers_order'),
)
inline_stickers_next = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_stickers_next.insert(i)

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['reviews'], "https://t.me/+i90ASa8vozY0NjJi"),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:advertising_posts_order'),
)
inline_advertising_posts = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_advertising_posts.insert(i)

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['feedbacks'], 'https://t.me/+6SwP8pHNBERkOTYy'),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='services:content_for_your_channel_order'),
)
inline_content_for_your_channel = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_content_for_your_channel.insert(i)

buttons = config['Buttons']
stickers_order_1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
stickers_order_1.row(*[types.KeyboardButton(o) for o in [
buttons["anim_stickers"],
buttons["stat_stickers"],
]])

stickers_order_2 = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(buttons["skip_stickers"], callback_data="sticks_order:cancel"))

buttons = (
    types.InlineKeyboardButton(inline['anim_stickers'], callback_data='stickers:anim'),
    types.InlineKeyboardButton(inline['stat_stickers'], callback_data='stickers:stat'),
)
inline_anim_or_stat_stickers = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_anim_or_stat_stickers.insert(i)

buttons = config['Buttons']
cont_f_u_1 = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(buttons["skip_stickers"], callback_data="cont_f_u:cancel"))


buttons = (
    types.InlineKeyboardButton("1-3", callback_data='order_cont_posts:1-3'),
    types.InlineKeyboardButton("4-10", callback_data='order_cont_posts:4-10'),
    types.InlineKeyboardButton("11 и больше", callback_data='order_cont_posts:11+'),
)
inline_order_cont_posts = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_order_cont_posts.insert(i)

buttons = (
    types.InlineKeyboardButton(inline['anim'], callback_data='chan_des:anim'),
    types.InlineKeyboardButton(inline['stat'], callback_data='chan_des:stat'),
)
inline_anim_or_stat_chan_des = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_anim_or_stat_chan_des.insert(i)

buttons = config['Buttons']
chan_des_order_2 = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(buttons["skip_stickers"], callback_data="chan_order:cancel"))

buttons = config['Buttons']
inline_ad_p = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(buttons["skip_stickers"], callback_data="ad_psts:cancel"))

buttons = (
    types.InlineKeyboardButton(inline['ask_a_question'], callback_data='services:ask'),
    types.InlineKeyboardButton(inline['order_a_service'], callback_data='start:2'),
)
inline_start2 = types.InlineKeyboardMarkup(row_width=2)
for i in buttons:
    inline_start2.insert(i)

inline_new_start = types.InlineKeyboardMarkup()
# inline_new_start.add(types.InlineKeyboardButton("Обучение", callback_data="start:1"))
inline_new_start.add(types.InlineKeyboardButton("Открыть меню", callback_data="menu"))

