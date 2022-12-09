from aiogram import types
import keyboards
from aiogram.dispatcher import FSMContext
import states
import datetime
from data import db

from loader import dp


@dp.callback_query_handler(keyboards.callbacks.call_add_note.filter())
async def add_note(query: types.CallbackQuery, callback_data: dict):
    day = callback_data.get("day")
    month = callback_data.get("month")
    year = callback_data.get("year")
    user_id = callback_data.get("id")
    day, month, year, user_id = map(int, (day, month, year, user_id))
    message = query.message
    await states.AddNote.time.set()
    state = dp.get_current().current_state()
    await state.update_data(date=f"{day}.{month}.{year}")
    await message.answer("Напишите время(в формате ЧЧ:ММ)")


def check_time(text):
    try:
        datetime.datetime.strptime(text, "%H:%M")
        return True
    except ValueError:
        return False


@dp.message_handler(lambda message: not check_time(message.text), state=states.AddNote.time)
async def process_error_time(message: types.Message, state: FSMContext):
    await message.reply('Неправильный формат времени, нужно в формате "ЧЧ:ММ". Повторите попытку снова.')


@dp.message_handler(state=states.AddNote.note)
async def process_note(message: types.Message, state: FSMContext):
    note = message.text
    userid = message.chat.id
    async with state.proxy() as data:
        time = data['time']
        date = data['date']
        note_datetime = datetime.datetime.strptime(f"{date} {time}", "%d.%m.%Y %H:%M")

    db.add_note(userid, note_datetime, note)

    await state.finish()
    await message.answer("Добавлено!")


@dp.message_handler(state=states.AddNote.time)
async def process_time(message: types.Message, state: FSMContext):
    time = message.text
    async with state.proxy() as data:
        data['time'] = message.text

    await states.AddNote.note.set()
    await message.reply("А теперь отправьте описание:")
