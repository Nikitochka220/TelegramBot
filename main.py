import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update, context):
    await update.message.reply_text("Бот работает!")

app = ApplicationBuilder().token(os.getenv("TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
