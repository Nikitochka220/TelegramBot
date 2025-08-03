import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# Получаем токен из переменных окружения (Render > Environment Variables)
TOKEN = os.getenv("TOKEN")

# Создаем приложение
app = ApplicationBuilder().token(TOKEN).build()

# Хендлер команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 Сделать аву", callback_data="make_ava")],
        [InlineKeyboardButton("🤖 Сделать бота", callback_data="make_bot")],
        [InlineKeyboardButton("⭐ Оставить отзыв", callback_data="leave_review")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.first_name or 'друг'}!\n"
        "Чем тебе помочь?",
        reply_markup=markup
    )

# Хендлер нажатия кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    match query.data:
        case "make_ava":
            await query.message.reply_text("✏️ Напишите подробно, что вы хотите на аватарке.")
        case "make_bot":
            await query.message.reply_text("🤖 На какую тему вы хотите создать бота?")
        case "leave_review":
            await query.message.reply_text("📝 Напишите отзыв и мы обязательно его учтём.")
        case _:
            await query.message.reply_text("❓ Неизвестное действие.")

# Регистрируем хендлеры
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_button))

# Запуск бота
if __name__ == "__main__":
    app.run_polling()

