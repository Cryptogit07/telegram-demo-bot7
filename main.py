# =========================================================
#  Telegram Demo Bot – Render-friendly version (Free Plan)
# =========================================================
import asyncio
import json
import os
from threading import Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ---------------------------------------------------------
# 🟢  Keep-Alive Web Server for Render Free Tier
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask).start()
# ---------------------------------------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")

CHANNELS = {
    "📺 Apomind": -1003024587412,
    "🎓 Gyanlive Senior SA": -1003074082140,
    "🧠 Praajasv": -1003045912098,
    "🏛️ All India Foundation Sanus 2.0": -1003072859108,
    "🔬 Laboratory Assistant": -1002792750144,
    "💻 WebsankulLive TET-TAT Live": -1002850657043,
    "📚 Websankul Class 3": -1003010026364,
    "🗣️ Webdemy English Prelims + Mains": -1002890011973,
    "💪 Dhairya 2.0 Paid": -1002991324208,
    "🚀 Sambhav 3.0": -1002943485756
}

USER_DATA_FILE = "user_data.json"

def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=name)]
        for name in CHANNELS.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome! Choose which channel demo you'd like to try:\n\n"
        "Each demo lasts 2 minutes and can only be taken once per channel.",
        reply_markup=reply_markup,
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    channel_name = query.data
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = []

    if channel_name in user_data[user_id]:
        await query.answer("❌ You already took this demo.")
        return

    user_data[user_id].append(channel_name)
    save_user_data(user_data)

    await query.answer()
    await query.edit_message_text(f"✅ Adding you to {channel_name} for 2 minutes...")

    channel_id = CHANNELS[channel_name]

    try:
        await context.bot.add_chat_member(chat_id=channel_id, user_id=user_id)
        await asyncio.sleep(120)
        await context.bot.ban_chat_member(chat_id=channel_id, user_id=user_id)
        await context.bot.unban_chat_member(chat_id=channel_id, user_id=user_id)
        await context.bot.send_message(chat_id=user_id,
                                       text=f"⏰ Your demo for {channel_name} has ended.")
    except Exception as e:
        await context.bot.send_message(chat_id=user_id,
                                       text=f"⚠️ Error while adding/removing you: {e}")

async def main():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_click))
    print("🤖 Bot is running... (Render free plan + Flask alive)")
    await app_bot.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
