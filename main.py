from telegram.ext import ApplicationBuilder
from telegram.ext import ApplicationBuilder, CommandHandler
import os

async def start(update, context):
    await update.message.reply_text("✅ Бот запущен и работает!")

app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()  # <=== ОБЯЗАТЕЛЬНО! Не удаляй!
