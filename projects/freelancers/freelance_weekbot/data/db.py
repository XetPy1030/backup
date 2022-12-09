import datetime
import sqlite3
import json

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()


def create_table():
    cursor.execute("""
CREATE TABLE users (
    id INT PRIMARY KEY,
    data TEXT DEFAULT '{"notes":[]}'
);
""")
    conn.commit()


def new_user(id: int):
    data = {
        "notes": [
            {
                "name": "Тестовая заметка",
                "date": "04.07.2022",
                "time": "14:00"
            }
        ]
        }

    cursor.execute("INSERT OR REPLACE INTO users VALUES(?, ?)", (id,'{"notes":[]}'))
    conn.commit()

    return data


def get_users():
    cursor.execute("SELECT * FROM users")
    ret = cursor.fetchall()
    return [{"id": i[0], "data": json.loads(i[1])} for i in ret] if len(ret) else {}


def get_data_user(id: int):
    cursor.execute("SELECT * FROM users WHERE id=?", (id,))
    ret = cursor.fetchall()
    return json.loads(ret[0][1]) if len(ret) else new_user(id)


def set_user(id: int, data: dict):
    cursor.execute("INSERT OR REPLACE INTO users VALUES(?, ?)", (id, json.dumps(data)))
    conn.commit()


def get_notes_user_from_date(id: int, date: datetime.date):
    user = get_data_user(id)
    txt_date = date.strftime("%d.%m.%Y")
    notes = []
    for i in user['notes']:
        if i['date'] == txt_date:
            notes.append(i)
    return notes


def get_notes_user_from_datetime(id: int, datetime: datetime.datetime):
    user = get_data_user(id)
    txt_date = datetime.strftime("%d.%m.%Y")
    txt_time = datetime.strftime("%H:%M")
    notes = []
    for i in user['notes']:
        if i['date'] == txt_date and i['time'] == txt_time:
            notes.append(i)
    return notes


def del_note_from_date_and_num(id: int, date: datetime.date, num: int):
    user = get_data_user(id)
    txt_date = date.strftime("%d.%m.%Y")
    notes = []
    notes_day = []
    for i in user['notes']:
        if i['date'] == txt_date:
            notes_day.append(i)
        else:
            notes.append(notes)
    notes_day.pop(num)
    notes.extend(notes_day)
    user['notes'] = notes
    set_user(id, user)


def add_note(id: int, note_datetime: datetime.datetime, note: str):
    user = get_data_user(id)
    date = note_datetime.strftime("%d.%m.%Y")
    time = note_datetime.strftime("%H:%M")
    user['notes'].append({
        "name": note,
        "date": date,
        "time": time
    })
    set_user(id, user)
