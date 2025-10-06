import asyncio
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# -------------------------------------------------------------
# 🔐 BOT TOKEN — Loaded from Replit Secret (DON'T hardcode)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# -------------------------------------------------------------

# 🏠 YOUR 10 CHANNELS (use the IDs you provided)
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

# 📁 File to store which users took which demos
USER_DATA_FILE = "user_data.json"

# -------------------- Helper Functions -----------------------

def load_user_data():
    """Load user demo history from file."""
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    """Save user demo history to file."""
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

# -------------------- Bot Commands ----------------------------

# 🚀 /start command — shows available demo channels
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=name)] for name in CHANNELS.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome! Choose which channel demo you'd like to try:\n\n"
        "Each demo lasts 2 minutes and can only be taken once per channel.",
        reply_markup=reply_markup,
    )

# ⚡ When user taps a button
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    channel_name = query.data
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = []

    # If user already took that channel demo
    if channel_name in user_data[user_id]:
        await query.answer("❌ You already took this demo.")
        return

    # Add record to user data
    user_data[user_id].append(channel_name)
    save_user_data(user_data)

    await query.answer()
    await query.edit_message_text(f"✅ Generating your demo link for {channel_name}...")

    channel_id = CHANNELS[channel_name]

    try:
        # Create a one-time invite link that expires in 2 minutes
        import datetime
        expire_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
        
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=channel_id,
            member_limit=1,
            expire_date=expire_time
        )

        # Send the invite link to the user
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 Click the link below to join {channel_name}:\n\n"
                 f"{invite_link.invite_link}\n\n"
                 f"⏰ This link expires in 2 minutes and works only once!"
        )

        # Wait for 2 minutes
        await asyncio.sleep(120)

        # Remove the user from the channel after 2 minutes
        try:
            await context.bot.ban_chat_member(chat_id=channel_id, user_id=int(user_id))
            await context.bot.unban_chat_member(chat_id=channel_id, user_id=int(user_id))
        except Exception as remove_error:
            print(f"Error removing user {user_id}: {remove_error}")

        # Revoke the invite link after 2 minutes
        await context.bot.revoke_chat_invite_link(
            chat_id=channel_id,
            invite_link=invite_link.invite_link
        )

        # Notify user that demo period ended
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⏰ Your 2-minute demo for {channel_name} has ended.\n"
                 f"You have been removed from the channel."
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⚠️ Sorry, there was an error: {e}",
        )

# -------------------- Run the Bot ------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🤖 Bot is running... Press Stop to quit.")
    app.run_polling()

if __name__ == "__main__":
    main()
