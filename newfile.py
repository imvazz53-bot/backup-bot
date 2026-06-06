import telebot
from telebot import types
import json
import os

TOKEN = os.getenv("TOKEN_BOT")
print("TOKEN =", TOKEN)
ADMIN_ID = 8205606321

bot = telebot.TeleBot(TOKEN)

DB_FILE = "backup.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "files": []}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    data = load_db()

    uid = str(message.from_user.id)

    if uid not in data["users"]:
        data["users"][uid] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username
        }
        save_db(data)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("📸 Kirim Foto")
    markup.add("🎥 Kirim Video")
    markup.add("📂 Backup Saya")
    markup.add("ℹ️ Bantuan")

    bot.send_message(
        message.chat.id,
        """
🔐 Selamat Datang di Backup Bot

Simpan foto dan video penting Anda dengan mudah.

📸 Kirim Foto
🎥 Kirim Video
📂 Backup Saya
ℹ️ Bantuan

Semua file yang Anda kirim akan tersimpan sebagai cadangan.
""",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "ℹ️ Bantuan")
def bantuan(message):
    bot.reply_to(
        message,
        """
📌 Cara Penggunaan

1. Kirim foto atau video.
2. File akan tersimpan.
3. Gunakan /mybackup untuk melihat backup Anda.
"""
    )

@bot.message_handler(content_types=['photo'])
def save_photo(message):

    data = load_db()

    data["files"].append({
        "user_id": message.from_user.id,
        "name": message.from_user.first_name,
        "type": "photo",
        "file_id": message.photo[-1].file_id
    })

    save_db(data)

    bot.reply_to(
        message,
        "✅ Foto berhasil dibackup."
    )

@bot.message_handler(content_types=['video'])
def save_video(message):

    data = load_db()

    data["files"].append({
        "user_id": message.from_user.id,
        "name": message.from_user.first_name,
        "type": "video",
        "file_id": message.video.file_id
    })

    save_db(data)

    bot.reply_to(
        message,
        "✅ Video berhasil dibackup."
    )

@bot.message_handler(commands=['mybackup'])
def mybackup(message):

    data = load_db()

    found = False

    for item in data["files"]:

        if item["user_id"] == message.from_user.id:

            found = True

            if item["type"] == "photo":
                bot.send_photo(
                    message.chat.id,
                    item["file_id"]
                )

            elif item["type"] == "video":
                bot.send_video(
                    message.chat.id,
                    item["file_id"]
                )

    if not found:
        bot.send_message(
            message.chat.id,
            "📂 Anda belum memiliki backup."
        )

@bot.message_handler(commands=['saya'])
def users(message):

    if message.from_user.id != ADMIN_ID:
        return

    data = load_db()

    text = "👥 DAFTAR PENGGUNA\n\n"

    for uid, info in data["users"].items():

        text += (
            f"Nama: {info['name']}\n"
            f"ID: {uid}\n"
            f"Username: @{info['username']}\n\n"
        )

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['backup'])
def backup(message):

    if message.from_user.id != ADMIN_ID:
        return

    data = load_db()

    for item in data["files"]:

        caption = (
            f"Pengguna: {item['name']}\n"
            f"ID: {item['user_id']}"
        )

        if item["type"] == "photo":
            bot.send_photo(
                message.chat.id,
                item["file_id"],
                caption=caption
            )

        elif item["type"] == "video":
            bot.send_video(
                message.chat.id,
                item["file_id"],
                caption=caption)
# 
=# ======================
# RUN BOT (RAILWAY FIX)
# ======================
print("🚀 Backup Bot Aktif...")

bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60
)
