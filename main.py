import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

TOKEN = os.getenv("TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

# Пример команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Сделать аву", callback_data="make_ava")],
        [InlineKeyboardButton("Сделать бота", callback_data="make_bot")],
        [InlineKeyboardButton("Оставить отзыв", callback_data="leave_review")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name or 'друг'}!\nЧем тебе помочь?",
        reply_markup=markup
    )

# Заглушка для обработки кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"Вы выбрали: {query.data}")

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_button))

app.run_polling()

