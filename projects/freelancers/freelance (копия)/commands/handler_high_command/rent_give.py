from core import dp, bot
import utils.db as db
from aiogram import types
from data import lang, markups, states
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(lambda c: c.data == "rent_give")
async def rent_give_func(inline_query: types.CallbackQuery):
    message = inline_query.message
    await message.answer(lang.rent_give_message)
    await states.RentGiveForm.city.set()
    await message.answer(lang.state_city)


@dp.message_handler(state=states.RentGiveForm.city)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    await states.RentGiveForm.next()
    await message.reply(lang.state_is_long_time, reply_markup=markups.button_rent_is_long_time)


@dp.message_handler(state=states.RentGiveForm.is_long_time)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['is_long_time'] = message.text

    await states.RentGiveForm.next()
    await message.reply(lang.state_price, reply_markup=markups.button_null)


@dp.message_handler(state=states.RentGiveForm.price)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

    await states.RentGiveForm.next()
    await message.reply(
        lang.state_num_rooms
    )


@dp.message_handler(state=states.RentGiveForm.num_rooms)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['num_rooms'] = message.text

    await states.RentGiveForm.next()
    await message.reply(lang.state_send_photos, reply_markup=markups.button_null)


@dp.message_handler(state=states.RentGiveForm.photos, content_types=["photo"])
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photos'] = message.text

        markup = types.ReplyKeyboardRemove()

        db.new_rent(
            message.chat.id,
            data['city'],
            data['is_long_time'] == lang.rents_time[1],
            data['price'],
        )
        await message.answer(
            "Готово!",
            reply_markup=markup
        )

        await message.answer(
            lang.form_rent.format(
                user = f'<a href="tg://user?id={message.chat.id}">{message.chat.full_name}</a>',
                city = data['city'],
                type = data['is_long_time'],
                price = data['price'],
                ),
            reply_markup=markup
        )

    await state.finish()