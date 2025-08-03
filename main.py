from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import json
import os

TOKEN = '8364031177:AAElNQeyoZTzaiR5vyRNHF5ui-fBxK9eN38'
ADMIN_CHAT_ID = 7216669628
CHANNEL_USERNAME = '@NonalyHelp'

user_state = {}
user_ids = {}
blocked_users = set()
orders = []

if os.path.exists("orders.json"):
    with open("orders.json", "r") as f:
        try:
            orders = json.load(f)
        except json.JSONDecodeError:
            orders = []

main_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🎨 Сделать аву", callback_data="make_ava"),
        InlineKeyboardButton("🤖 Сделать бота", callback_data="make_bot")
    ],
    [
        InlineKeyboardButton("🌍 Карта RobloxStudio", callback_data="make_map"),
        InlineKeyboardButton("🌐 Сайт (HTML/CSS/JS)", callback_data="make_website")
    ],
    [
        InlineKeyboardButton("✍️ Оставить отзыв", callback_data="leave_review"),
        InlineKeyboardButton("📦 Мои заявки", callback_data="my_orders")
    ]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_ids[user.username or str(user.id)] = user.id

    if user.id in blocked_users:
        await update.message.reply_text("⛔ Вы заблокированы и не можете пользоваться ботом.")
        return

    await update.message.reply_text(
        f"👋 Привет, {user.first_name or 'друг'}!\n\n💬 Чем тебе помочь?\n\n💡 Из-за того что у нас пока мало людей, все услуги бесплатны. Как только нас станет больше — перейдём на платный формат 💰",
        reply_markup=main_keyboard
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or str(user_id)

    if query.data == "make_ava":
        user_state[user_id] = "awaiting_ava_text"
        await query.message.reply_text("🎨 Что ты хочешь на аватарке?")

    elif query.data == "make_bot":
        user_state[user_id] = "awaiting_bot_text"
        await query.message.reply_text("🤖 Какой бот тебе нужен?")

    elif query.data == "make_map":
        user_state[user_id] = "awaiting_map_text"
        await query.message.reply_text("🌍 Опиши карту, которую хочешь в RobloxStudio")

    elif query.data == "make_website":
        user_state[user_id] = "awaiting_website_text"
        await query.message.reply_text("🌐 Что должен делать сайт?")

    elif query.data == "leave_review":
        user_state[user_id] = "awaiting_review"
        await query.message.reply_text("✍️ Напиши свой отзыв. После отзыва бот спросит твою оценку (1-5):")

    elif query.data == "my_orders":
        my = [o for o in orders if o['user_id'] == user_id]
        if not my:
            await query.message.reply_text("📭 У тебя пока нет заказов.")
        else:
            for i, o in enumerate(my, 1):
                status = o.get("status", "в процессе")
                await query.message.reply_text(f"{i}. {o['type']} — {o['text']} — {status}\n📝 Для изменения напиши новую версию заявки, или /cancel для отмены.")
                user_state[user_id] = f"editing_{i-1}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or str(user_id)
    text = update.message.text
    state = user_state.get(user_id)

    if state == "awaiting_review":
        context.user_data['review_text'] = text
        user_state[user_id] = "awaiting_rating"
        await update.message.reply_text("📊 Поставь оценку от 1 до 5:")
        return

    if state == "awaiting_rating":
        if text not in ['1', '2', '3', '4', '5']:
            await update.message.reply_text("❗ Введи число от 1 до 5")
            return
        review = context.user_data.get('review_text', '')
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⭐ Отзыв от @{username}:\n{review}\nОценка: {text}/5"
        )
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=f"📣 Новый отзыв от @{username}:\n{review}\nОценка: {text}/5"
        )
        await update.message.reply_text("✅ Спасибо за отзыв!")
        user_state[user_id] = None
        return

    if state and state.startswith("awaiting_"):
        order_type = state.replace("awaiting_", "").replace("_text", "")
        new_order = {
            "user_id": user_id,
            "user": username,
            "type": order_type,
            "text": text,
            "status": "в процессе"
        }
        orders.append(new_order)
        with open("orders.json", "w") as f:
            json.dump(orders, f)

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📥 Новый заказ [{order_type}] от @{username}:\n{text}"
        )
        await update.message.reply_text("✅ Заказ принят в работу!")
        user_state[user_id] = None

    elif state and state.startswith("editing_"):
        index = int(state.split("_")[1])
        if 0 <= index < len(orders) and orders[index]['user_id'] == user_id:
            orders[index]['text'] = text
            with open("orders.json", "w") as f:
                json.dump(orders, f)
            await update.message.reply_text("✏️ Заявка обновлена!")
        else:
            await update.message.reply_text("❗ Не удалось найти заявку для редактирования.")
        user_state[user_id] = None

async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    users = {o['user']: o['user_id'] for o in orders}
    message = "👥 Пользователи, оформлявшие заявки:\n"
    for name, uid in users.items():
        message += f"@{name} — {uid}\n"
    await update.message.reply_text(message)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    await update.message.reply_text("⚙️ Админ-панель активна. Все основные функции доступны через команды или сообщения.")

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("❗ Использование: /send <user_id> <сообщение>")
        return
    try:
        user_id = int(context.args[0])
        msg = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=msg)
        await update.message.reply_text("✅ Сообщение отправлено.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    if not context.args:
        await update.message.reply_text("❗ Использование: /broadcast <сообщение>")
        return
    msg = " ".join(context.args)
    sent = 0
    for uid in set(user_ids.values()):
        try:
            await context.bot.send_message(chat_id=uid, text=msg)
            sent += 1
        except:
            pass
    await update.message.reply_text(f"📨 Рассылка завершена. Отправлено: {sent}.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("user", user_command))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CommandHandler("send", send_command))
app.add_handler(CommandHandler("broadcast", broadcast_command))
app.add_handler(CallbackQueryHandler(handle_button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
