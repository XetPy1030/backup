from datetime import datetime
import sqlite3
import json

conn = sqlite3.connect('data/database.sqlite')
cursor = conn.cursor()


def new_user(id: int):
    data = {
        "status": "",
        "statistics": {
            "pressed_services": False,
            "pressed_feedbacks": False,
            "pressed_partners": False,
            "start_time": int(datetime.now().timestamp()),
            "update_time": int(datetime.now().timestamp()),
        },
        "admin": False,
        "from": None,
        "new_users": []
        }
    cursor.execute("INSERT OR REPLACE INTO users VALUES(?, ?)", (id, json.dumps(data)))
    conn.commit()
    return data


def new_user_from_old(id, from_user):
    user = new_user(id)
    user["from"] = from_user
    old_user = get_user(from_user)
    old_user["new_users"].append(id)
    set_user(id, user)
    set_user(from_user, old_user)


def set_admin(id, is_admin):
    user = get_user(id)
    user["admin"] = is_admin
    set_user(id, user)


def is_user(id):
    cursor.execute("SELECT * FROM users WHERE userid=?", (id,))
    ret = cursor.fetchall()
    # print(len(ret), ret)
    return bool(len(ret))


def get_users():
    cursor.execute("SELECT * FROM users")
    ret = cursor.fetchall()
    return [{"id": i[0], "data": json.loads(i[1])} for i in ret] if len(ret) else {}


def get_user(id: int):
    cursor.execute("SELECT * FROM users WHERE userid=?", (id,))
    ret = cursor.fetchall()
    return json.loads(ret[0][1]) if len(ret) else new_user(id)


def update_user(id: int):
    user = get_user(id)
    user['statistics'].update({'update_time': int(datetime.now().timestamp())})
    #user['statistics']['update_time'] = ),
    set_user(id, user)


def get_user_times(id: int):
    user = get_user(id)
    return {'started': datetime.fromtimestamp(user['statistics']['start_time']), 'updated': datetime.fromtimestamp(user['statistics']['update_time'])}


def get_user_with_true_statistics(id: int, param: str):
    users = []
    all_users = get_users()
    for i in all_users:
        if i['data']['statistics'][param]:
            users.append(i)
    return users


def get_users_with_true_statistics():
    users = []
    all_users = get_users()
    for i in all_users:
        if i['data']['statistics']['pressed_services'] or i['data']['statistics']['pressed_feedbacks'] or i['data']['statistics']['pressed_partners']:
            users.append(i)
            continue
    return users


def set_user(id: int, data: dict):
    cursor.execute("INSERT OR REPLACE INTO users VALUES(?, ?)", (id, json.dumps(data)))
    conn.commit()


def is_admin(id: int):
    return get_user(id)['admin']


def update_statistics(id: int, new_statistics: dict):
    user = get_user(id)
    user['statistics'].update(new_statistics)
    set_user(id, user)


def get_status(id: int):
    user = get_user(id)
    return user['status'] if len(user) else ''


def set_status(id: int, status=''):
    user = get_user(id)
    user['status'] = status
    cursor.execute("INSERT OR REPLACE INTO users VALUES(?, ?)", (id, json.dumps(user)))
    conn.commit()


def close():
    conn.close()

#new_user(1)
# update_user(1)
