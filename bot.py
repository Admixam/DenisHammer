import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = '7514163342:AAFBkgAcBCvtCvev93talMVgI9Fyl20hVug'
DATA_FILE = 'media_db.json'

# Загрузка базы
try:
    with open(DATA_FILE, 'r') as f:
        media_db = json.load(f)
except FileNotFoundError:
    media_db = {}

logging.basicConfig(level=logging.INFO)

# Проверка медиа на дубликат
async def check_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    user_mention = f"@{user.username}" if user.username else user.full_name

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
        first_message_id = media_db[unique_id]["message_id"]
        original_user = media_db[unique_id]["user"]
        # Бот отвечает на оригинал, а не на дубль
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=f"У нас ДЕНИС! ЭТО НЕ УЧЕБНАЯ ТРЕВОГА!
😡 {user_mention}, ты теперь официально — Денис",
            reply_to_message_id=first_message_id
        )
    else:
        media_db[unique_id] = {
            "message_id": message.message_id,
            "user": user_mention
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(media_db, f)

# Команда /проверка
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Я на месте, патрулирую мемы!")

# Запуск бота
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("проверка", check_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, check_media))
    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
