import configparser
import utils.markups as markups, utils.db as db


def button_menu_choice(id: int):
    return markups.button_menu_with_admin if db.is_admin(id) else markups.button_menu


config = configparser.ConfigParser()
config.read("./config.ini")

buttons = config['Buttons']
lang = config['Language']
inline = config['Inline']

reversed_buttons = {}
for i in dict(buttons).keys():
    reversed_buttons[buttons[i]] = i

reversed_lang = {}
for i in dict(lang).keys():
    reversed_lang[lang[i]] = i

__all__ = ["lang", "button_menu_choice", "reversed_buttons", "reversed_lang", "inline"]
