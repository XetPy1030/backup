from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime


def generate_confirm_markup(user_id: int, date: datetime.date):
    note_action_markup = InlineKeyboardMarkup()
    # создаём инлайн клавиатуру
    confirm_user_markup = InlineKeyboardMarkup(row_width=NUM_BUTTONS)
    for emoji in subjects:
        button = InlineKeyboardButton(
            text=emoji.unicode,
            callback_data=confirming_callback.new(subject=emoji.subject, necessary_subject=necessary_subject.subject, user_id=user_id)
        )
        confirm_user_markup.insert(button)

    # отдаём клавиатуру после создания
    return confirm_user_markup, necessary_subject.name
