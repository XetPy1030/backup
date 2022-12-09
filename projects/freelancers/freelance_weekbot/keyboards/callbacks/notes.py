from aiogram.utils.callback_data import CallbackData

note_standart = ("day", "month", "year", "id")
call_open_note = CallbackData("note", *note_standart)
call_add_note = CallbackData("noteAdd", *note_standart)
call_delete_note = CallbackData("noteDelete", *note_standart)
call_edit_note = CallbackData("noteEdit", *note_standart)
