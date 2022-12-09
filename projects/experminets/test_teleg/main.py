from pyrogram import (
    Client,
    filters
    )
import pyrogram
from pyrogram.handlers import (
    message_handler
)

bot = Client(
    'bot',
    api_id=18936848,
    api_hash="4da77bed845aebdfeceb62e83533d7f0",
    bot_token="5488863430:AAFsNYw_eaFQPr-eyR3B3O8-i8LsVUDrz2g"
)


@bot.on_message(filters.text)
def status_handler(client: pyrogram.client.Client,
                   message: pyrogram.types.messages_and_media.message.Message):
    pass


bot.run()
