import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = '7514163342:AAFBkgAcBCvtCvev93talMVgI9Fyl20hVug'
DATA_FILE = 'media_db.json'

try:
    with open(DATA_FILE, 'r') as f:
        media_db = json.load(f)
except FileNotFoundError:
    media_db = {}

logging.basicConfig(level=logging.INFO)

async def check_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    media = None
    if message.photo:
        media = message.photo[-1]
    elif message.video:
        media = message.video
    elif message.animation:
        media = message.animation
    else:
        return

    unique_id = media.file_unique_id

    if unique_id in media_db:
        first_message_id = media_db[unique_id]
        await message.reply_text("У нас ДЕНИС! ЭТО НЕ УЧЕБНАЯ ТРЕВОГА!")
        await context.bot.forward_message(
            chat_id=message.chat_id,
            from_chat_id=message.chat_id,
            message_id=first_message_id
        )
    else:
        media_db[unique_id] = message.message_id
        with open(DATA_FILE, 'w') as f:
            json.dump(media_db, f)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, check_media))
    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
