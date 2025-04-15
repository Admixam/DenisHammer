import logging
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = '7514163342:AAFBkgAcBCvtCvev93talMVgI9Fyl20hVug'
DATA_FILE = 'media_db.json'
PORT = int(os.environ.get('PORT', '10000'))

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
        try:
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=f"У нас ДЕНИС! ЭТО НЕ УЧЕБНАЯ ТРЕВОГА!
😡 {user_mention}, ты теперь официально — Денис",
                reply_to_message_id=first_message_id
            )
        except Exception as e:
            logging.warning(f"Не удалось ответить на оригинал: {e}")
            await message.reply_text(
                f"У нас ДЕНИС! ЭТО НЕ УЧЕБНАЯ ТРЕВОГА!
😡 {user_mention}, ты теперь официально — Денис"
            )
    else:
        media_db[unique_id] = {
            "message_id": message.message_id,
            "user": user_mention
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(media_db, f)

# /check команда
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Я на месте, патрулирую мемы!")

# Запуск Webhook-сервера
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, check_media))

    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    print(f"Запуск по Webhook: {webhook_url}")
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
