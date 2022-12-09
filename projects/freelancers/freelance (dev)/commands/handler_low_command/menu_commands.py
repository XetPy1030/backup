from core import dp, bot
import utils.db as db
import utils.markups as markups
from utils import generate_inline_services
from config import buttons, lang, config
import asyncio
from aiogram import filters, types


@dp.message_handler(filters.Text(buttons['our_services']))
async def do_our_services(message: types.Message):
    db.update_statistics(message.chat.id, {'pressed_services': True})
    await bot.send_photo(message.chat.id,
                         photo=open('./new_photos/services.png', 'rb'),
                         caption=lang['our_services'],
                         reply_markup=generate_inline_services.generate_services_inline()
                         )


@dp.callback_query_handler(status_inline='services_next')
async def dgcv(inline_query: types.CallbackQuery):
    await inline_query.message.edit_reply_markup(generate_inline_services.generate_services_inline(
        int(inline_query.data.split(":")[1])
    ))


@dp.message_handler(filters.Text(buttons['our_partners']))
async def do_our_partners(message: types.Message):
    db.update_statistics(message.chat.id, {'pressed_partners': True})
    await message.answer_photo(open("photos/about.png", "rb"), caption=lang['about1'])
    await asyncio.sleep(4)
    await message.answer(lang['about2'])
    await asyncio.sleep(4)
    await message.answer_photo(open("photos/about2.png", "rb"), caption=lang['about3'] )


@dp.message_handler(filters.Text(buttons['reviews']))
async def do_reviews(message: types.Message):
    inline_kb = types.InlineKeyboardMarkup(row_width=2).add(
        types.InlineKeyboardButton(lang['reviews'], url=config['Links']['reviews'])
        )
    await message.answer_photo(open("photos/feedbacks.png", "rb"), caption=lang['feedback'], reply_markup=inline_kb)


@dp.message_handler(filters.Text(buttons['feedbacks']))
async def do_feedbacks(message: types.Message):
    db.update_statistics(message.chat.id, {'pressed_feedbacks': True})
    await message.answer_photo(open("new_photos/support.png", "rb"), caption=lang['feedback_ans'], reply_markup=markups.button_back)
    db.set_status(message.chat.id, 'feedback')
