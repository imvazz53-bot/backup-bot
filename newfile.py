import telebot
from telebot import types
import json
import os
import time

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan")

ADMIN_ID = 8205606321

bot = telebot.TeleBot(TOKEN)

DB_FILE = "backup.json"

# Membuat database jika belum ada
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": {}, "files": []}, f)


def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "users": {},
            "files": []
        }


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


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

Semua file yang Anda kirim akan tersimpan sebagai cadangan pribadi.
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
2. File akan tersimpan otomatis.
3. Gunakan /mybackup untuk melihat backup Anda.
"""
    )


@bot.message_handler(func=lambda m: m.text == "📸 Kirim Foto")
def tombol_foto(message):
    bot.send_message(
        message.chat.id,
        "📸 Silakan kirim foto yang ingin dibackup."
    )
    data = load_db()

    data["files"].append({
        "user_id": message.from_user.id,
        "name": message.from_user.first_name,
        "type": "photo",
        "file_id": message.photo[-1].file_id
    })

    save_db(data)

    bot.reply_to(message, "✅ Foto berhasil dibackup.")


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

    bot.reply_to(message, "✅ Video berhasil dibackup.")

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

@bot.message_handler(func=lambda m: m.text == "📂 Backup Saya")
def tombol_backup_saya(message):
    mybackup(message)


@bot.message_handler(commands=['saya'])
def users(message):

    if message.from_user.id != ADMIN_ID:
        return

    data = load_db()

    text = "👥 DAFTAR PENGGUNA\n\n"

    for uid, info in data["users"].items():

        username = info.get("username") or "-"

        text += (
            f"Nama: {info['name']}\n"
            f"ID: {uid}\n"
            f"Username: {username}\n\n"
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['backup'])
def backup(message):

    if message.from_user.id != ADMIN_ID:
        return

    data = load_db()

    if not data["files"]:
        bot.send_message(message.chat.id, "Belum ada file backup.")
        return

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
                caption=caption
            )


print("✅ Backup Bot Aktif...")

bot.remove_webhook()

while True:
    try:
        bot.infinity_polling(
            skip_pending=True,
            timeout=60,
            long_polling_timeout=60
        )

    except Exception as e:
        print("❌ Error:", e)
        print("🔄 Menghubungkan ulang dalam 10 detik...")
        time.sleep(10)
