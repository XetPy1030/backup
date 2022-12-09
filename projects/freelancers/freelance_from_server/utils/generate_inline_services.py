from . import markups
from aiogram import types
from config import inline


def generate_services_inline(page=1, per_page=5):
    texts = markups.texts_services[(page-1)*per_page:page*per_page]
    inline_for_services = types.InlineKeyboardMarkup(row_width=3)
    for i in texts:
        inline_for_services.add(
            types.InlineKeyboardButton(inline[i], callback_data=f'services:{i}')
            )

    other = []
    if page > 1:
        other.append(
            types.InlineKeyboardButton("<--", callback_data=f'services_next:{page-1}'),
            )
    else:
        other.append(
            types.InlineKeyboardButton("###", callback_data="no"),
            )
    other.append(
        types.InlineKeyboardButton(f"{page} из {len(markups.texts_services)//per_page+(1 if len(markups.texts_services)%per_page else 0) }", callback_data="no"),
    )
    if page <= len(markups.texts_services)//per_page and len(markups.texts_services)%per_page > 1:
        other.append(
            types.InlineKeyboardButton("-->", callback_data=f'services_next:{page+1}'),
            )
    else:
        other.append(
            types.InlineKeyboardButton("###", callback_data="no"),
            )
    inline_for_services.row(*other)
    return inline_for_services
