from datetime import datetime
import sqlite3
import json

conn = sqlite3.connect('data/database.sqlite')
cursor = conn.cursor()


def create_table():
    cursor.execute("CREATE TABLE rents (id VARCHAR(20), city VARCHAR(40), is_long_time BOOL, price VARCHAR(20), rooms TINYINT, photos TINYTEXT, data TEXT)")
    conn.commit()


def new_rent(id: int, city: str, is_long_time: bool, price: str, num_rooms: int, photos: list[str], data: dict = {}):
    cursor.execute("INSERT OR REPLACE INTO rents VALUES(?, ?, ?, ?, ?, ?, ?)", (
                                                                          id,
                                                                          city,
                                                                          is_long_time,
                                                                          price,
                                                                          num_rooms,
                                                                          ",".join(photos),
                                                                          json.dumps(data)
                                                                          ))
    conn.commit()
    return data


def is_user(id):
    cursor.execute("SELECT * FROM rents WHERE id=?", (id,))
    ret = cursor.fetchall()
    return bool(len(ret))


def get_rents(city: str, is_long_time: bool):
    cursor.execute("SELECT * FROM rents WHERE city=? AND is_long_time=?", (city, is_long_time))
    ret = cursor.fetchall()
    return ret
