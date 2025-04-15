import logging
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = '7514163342:AAFBkgAcBCvtCvev93talMVgI9Fyl20hVug'
DATA_FILE = 'media_db.json'
STATS_FILE = 'denis_stats.json'
PORT = int(os.environ.get('PORT', '10000'))

# Загрузка базы медиа
try:
    with open(DATA_FILE, 'r') as f:
        media_db = json.load(f)
except FileNotFoundError:
    media_db = {}

# Загрузка статистики
try:
    with open(STATS_FILE, 'r') as f:
        denis_stats = json.load(f)
except FileNotFoundError:
    denis_stats = {}

logging.basicConfig(level=logging.INFO)

def increment_denis(user_id, user_mention):
    if user_id not in denis_stats:
        denis_stats[user_id] = {"name": user_mention, "count": 0}
    denis_stats[user_id]["name"] = user_mention
    denis_stats[user_id]["count"] += 1
    with open(STATS_FILE, 'w') as f:
        json.dump(denis_stats, f)

async def top_denis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not denis_stats:
        await update.message.reply_text("Пока ни одного Дениса не обнаружено 😇")
        return

    sorted_stats = sorted(denis_stats.values(), key=lambda x: x["count"], reverse=True)
    text = "📊 Топ Денисов за всё время:\n\n"
    for i, entry in enumerate(sorted_stats[:10], start=1):
        text += f"{i}. {entry['name']} — {entry['count']} повторов\n"

    await update.message.reply_text(text)

async def check_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    user_mention = f"@{user.username}" if user.username else user.full_name
    username = user.username or ""

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
        increment_denis(str(user.id), user_mention)

        if username.lower() == "denisgobov":
            alert_text = "🔥 Уровень угрозы: ДЕНИС МАКСИМАЛЬНЫЙ!"
        else:
            alert_text = f"У нас ДЕНИС! ЭТО НЕ УЧЕБНАЯ ТРЕВОГА!\n😡 {user_mention}, ты теперь официально — Денис"

        try:
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=alert_text,
                reply_to_message_id=first_message_id
            )
        except Exception as e:
            logging.warning(f"Не удалось ответить на оригинал: {e}")
            await message.reply_text(alert_text)
    else:
        media_db[unique_id] = {
            "message_id": message.message_id,
            "user": user_mention
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(media_db, f)

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Я на месте, патрулирую мемы!")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("top_denisov", top_denis_command))
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
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Cannot close a running event loop" in str(e):
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.get_event_loop().run_until_complete(main())
        else:
            raise
