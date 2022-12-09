from core import dp, bot
import utils.db as db
from aiogram import types
from data import lang, markups, states
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(lambda c: c.data == "rent_get")
async def rent_give_func(inline_query: types.CallbackQuery):
    message = inline_query.message
    await message.answer(lang.rent_give_message)
    await states.RentGetForm.city.set()
    await message.answer(lang.state_city)


@dp.message_handler(state=states.RentGetForm.city)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    await states.RentGetForm.next()
    await message.reply(lang.state_is_long_time, reply_markup=markups.button_rent_is_long_time)


@dp.message_handler(state=states.RentGetForm.is_long_time)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        city = data['city']
    is_long_time = message.text

    await message.answer("Поиск..." , reply_markup=markups.button_null)

    rents = db.get_rents(city, is_long_time=is_long_time==lang.rents_time[1])
    for rent in rents:
        await message.answer(
            lang.form_rent.format(
                user = f'<a href="tg://user?id={rent[0]}">Пользователь</a>',
                city = rent[1],
                type = rent[2],
                price = rent[3],
                ),
        )

    await state.finish()
