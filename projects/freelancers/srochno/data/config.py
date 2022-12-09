import os

from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env("BOT_TOKEN")
ADMINS_ID = env.list("ADMINS_ID")


SKIP_UPDATES = env.bool("SKIP_UPDATES", False)

WORK_PATH = os.getcwd()
