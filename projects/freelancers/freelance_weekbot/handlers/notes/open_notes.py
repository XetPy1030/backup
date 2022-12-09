from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hbold
from loguru import logger
import datetime
from data import db
import keyboards

from loader import dp

call = keyboards.callbacks.call_open_note
weeks = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


@dp.message_handler(Command("open"), chat_type='private')
async def open_notes(message: types.Message):
    notes_inline = types.InlineKeyboardMarkup(row_width=1)
    date_now = datetime.date.today()
    day = datetime.timedelta(days=1)
    for i in range(7):
        notes = db.get_notes_user_from_date(message.chat.id, date_now)
        date_txt = date_now.strftime("%d.%m.%Y")
        notes_inline.insert(
            types.InlineKeyboardButton(
                text=f"{weeks[date_now.weekday()]} {date_txt} ({len(notes)})",
                callback_data=call.new(
                    day=date_now.day,
                    month=date_now.month,
                    year=date_now.year,
                    id=message.chat.id
                    )
            )
        )
        date_now += day
    # logger.debug(f"@{message.from_user.username}:{message.from_user.id} in default handler")

    await message.answer(
        text=''.join(
            (
                f"Привет, {hbold(message.from_user.full_name)}\n\n",
                "Нажми на кнопку, чтобы показать заметки на день",
            )
        ),
        reply_markup=notes_inline
    )


@dp.callback_query_handler(call.filter())
async def open_note(query: types.CallbackQuery, callback_data: dict):
    day = callback_data.get("day")
    month = callback_data.get("month")
    year = callback_data.get("year")
    user_id = callback_data.get("id")
    day, month, year, user_id = map(int, (day, month, year, user_id))
    message = query.message
    date = datetime.date(year, month, day)
    notes = db.get_notes_user_from_date(user_id, date)

    text = f"Заметки за {weeks[date.weekday()]} {date.strftime('%d.%m.%Y')}\n"
    if not len(notes):
        text += "Не найдено"

    for i in range(len(notes)):
        note = notes[i]
        text += "{num}. {time} {name}\n".format(
            num=i+1,
            time=note["time"],
            name=note["name"]
        )

    notes_inline = types.InlineKeyboardMarkup(row_width=1)
    kwargs = {
        "id": message.chat.id,
        "year": year,
        "month": month,
        "day": day
    }
    notes_inline.insert(types.InlineKeyboardButton(
        "Добавить заметку",
        callback_data=keyboards.callbacks.call_add_note.new(**kwargs)
    ))
    notes_inline.insert(types.InlineKeyboardButton(
        "Удалить заметку",
        callback_data=keyboards.callbacks.call_delete_note.new(**kwargs)
    ))
    notes_inline.insert(types.InlineKeyboardButton(
        "Изменить заметку",
        callback_data=keyboards.callbacks.call_edit_note.new(**kwargs)
    ))
    await message.answer(text, reply_markup=notes_inline)
