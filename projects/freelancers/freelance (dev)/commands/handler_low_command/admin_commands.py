from core import dp, bot
import utils.db as db
import utils.markups as markups
from config import buttons, lang, config
import asyncio
from datetime import timedelta, datetime
from aiogram import filters, types


@dp.message_handler(filters.Text(buttons['admin']), db_admin=[db, True])
async def admin_panel(message: types.Message):
    await message.answer(lang['admin'], reply_markup=markups.button_admin)


@dp.message_handler(filters.Text(buttons['statistics']), db_admin=[db, True])
async def statistics(message: types.Message):
    all_text = ''
    checks = [[7, 'неделю'], [30, 'месяц']]
    for i in checks:
        days, text = i
        stat_new_users_for_time = 0
        stat_active_for_time = 0
        stat_not_active_for_time = 0
        for user in db.get_users():
            # print(user)
            times = db.get_user_times(user['id'])
            time_now = datetime.now()
            stat_new_users_for_time += (time_now-times['started'])<timedelta(days=days)
            stat_active_for_time += (time_now-times['updated']).days < days
            stat_not_active_for_time += (time_now-times['updated']).days > days
        all_text += "\n".join([
            f"Кол-во новых участников за {text}: {stat_new_users_for_time}",
            f"Кол-во активных участников за {text}: {stat_active_for_time}",
            # f"Кол-во неактивных участников за {text}: {stat_not_active_for_time}",
            ""])+'\n'
    all_text += f"Всего пользователей: {len(db.get_users())}\n"
    all_text += f"Нажали хоть что-то: {len(db.get_users_with_true_statistics())}\n"
    all_text += f"Купивши обучение: {len(db.get_users_with_train())}"
    await message.answer(all_text)


@dp.message_handler(filters.Text(buttons['mailing']), db_admin=[db, True])
async def mailing(message: types.Message):
    db.set_status(message.chat.id, 'mailing:choice')
    await message.answer(lang['mailing'], reply_markup=markups.buttons_mailing)


@dp.message_handler(commands=['db'], db_admin=[db, True])
async def dbget(message: types.Message):
    await message.reply_document(open('./database.sqlite', 'rb'))
