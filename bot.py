# ═══════════════════════════════════════════════════════════
# 🤖 BOT TELEGRAM TẠO KEY — FULL FIX
# ═══════════════════════════════════════════════════════════
import telebot
from telebot import types
import time
import random
import string
import json
import os
import threading
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════
# CẤU HÌNH — SỬA DUY NHẤT Ở ĐÂY
# ═══════════════════════════════════════════════════════════
BOT_TOKEN = "8081809059:AAEV5cUJJ660gpKdLTlMta22Ary5pnRxy4Q"

# Để [] = ai cũng tạo key được
# Điền ID vào ví dụ [123456789] = chỉ admin
ADMIN_IDS = []

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.json")

bot = telebot.TeleBot(BOT_TOKEN)

# ═══════════════════════════════════════════════════════════
# LOCK + DATABASE
# ═══════════════════════════════════════════════════════════
_lock = threading.Lock()

def load_db():
    with _lock:
        if not os.path.exists(DB_FILE):
            return {}
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

def save_db(db):
    with _lock:
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Lỗi lưu DB: {e}")

def is_admin(uid):
    return len(ADMIN_IDS) == 0 or uid in ADMIN_IDS

def gen_key(prefix="VIP"):
    part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}-{part}"

# ═══════════════════════════════════════════════════════════
# MENU
# ═══════════════════════════════════════════════════════════
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔑 Key 1 Ngày", callback_data="quick_1"),
        types.InlineKeyboardButton("⚡ Key 7 Ngày", callback_data="quick_7"),
        types.InlineKeyboardButton("💎 Key 30 Ngày", callback_data="quick_30"),
        types.InlineKeyboardButton("👑 Key 365 Ngày", callback_data="quick_365"),
    )
    kb.add(
        types.InlineKeyboardButton("📋 Danh Sách Key", callback_data="list_keys"),
        types.InlineKeyboardButton("📊 Thống Kê", callback_data="stats"),
    )
    kb.add(
        types.InlineKeyboardButton("🆔 ID Của Tôi", callback_data="my_id"),
        types.InlineKeyboardButton("❓ Trợ Giúp", callback_data="help"),
    )
    return kb

def back_button():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Quay Lại Menu", callback_data="menu"))
    return kb

# ═══════════════════════════════════════════════════════════
# /start
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def cmd_start(msg):
    name = msg.from_user.first_name or "bạn"
    text = (
        f"🎮 *CÔNG CỤ HỖ TRỢ GAME — BOT TẠO KEY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Xin chào *{name}*!\n\n"
        f"✨ *CHỌN CHỨC NĂNG:*\n\n"
        f"🔑 `/newkey <ngày> <số>` — Tạo key\n"
        f"🔍 `/checkkey <key>` — Kiểm tra\n"
        f"📋 `/listkey` — Danh sách\n"
        f"🗑️ `/delkey <key>` — Xóa\n"
        f"🆔 `/myid` — Lấy ID\n"
        f"❓ `/help` — Trợ giúp\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Hoặc bấm nút bên dưới để tạo nhanh!*"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def cmd_help(msg):
    text = (
        "❓ *TRỢ GIÚP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔑 *Tạo Key:*\n"
        "`/newkey <số_ngày> <số_lượng>`\n"
        "📌 Ví dụ: `/newkey 7 3` → 3 key hạn 7 ngày\n\n"
        "🔍 *Kiểm Tra Key:*\n"
        "`/checkkey VIP-ABC123XYZ`\n\n"
        "📋 *Xem Danh Sách:* `/listkey`\n"
        "🗑️ *Xóa Key:* `/delkey VIP-ABC123XYZ`\n"
        "🆔 *Lấy ID:* `/myid`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *Copy key → nhập vào web!*"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=back_button())

# ═══════════════════════════════════════════════════════════
# TẠO KEY
# ═══════════════════════════════════════════════════════════
def create_keys(chat_id, days, qty, user_id):
    db = load_db()
    exp_time = time.time() + days * 86400
    exp_str = (datetime.now() + timedelta(days=days)).strftime("%d/%m/%Y %H:%M")
    keys_created = []

    for _ in range(qty):
        prefix = "VIP" if days >= 7 else "PRO"
        if days >= 365:
            prefix = "LUXURY"
        k = gen_key(prefix)
        while k in db:
            k = gen_key(prefix)
        db[k] = {
            "exp": exp_time,
            "days": days,
            "created": time.time(),
            "created_by": user_id
        }
        keys_created.append(k)

    save_db(db)

    text = (
        f"✅ *TẠO KEY THÀNH CÔNG!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Số lượng: *{qty} key*\n"
        f"⏰ Hạn dùng: *{days} ngày*\n"
        f"📅 Hết hạn: `{exp_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for k in keys_created:
        text += f"🔑 `{k}`\n"
    text += (
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Bấm vào key để copy*\n"
        f"🌐 *Dán vào web để kích hoạt!*"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['newkey'])
def cmd_newkey(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Bạn không có quyền tạo key!")
        return
    try:
        parts = msg.text.split()
        days = int(parts[1]) if len(parts) > 1 else 7
        qty = int(parts[2]) if len(parts) > 2 else 1
        days = max(1, min(days, 3650))
        qty = max(1, min(qty, 50))
    except:
        bot.reply_to(
            msg,
            "⚠️ *Cú pháp:* `/newkey <số_ngày> <số_lượng>`\n"
            "📌 *Ví dụ:* `/newkey 7 3` → 3 key hạn 7 ngày",
            parse_mode="Markdown"
        )
        return
    create_keys(msg.chat.id, days, qty, msg.from_user.id)

# ═══════════════════════════════════════════════════════════
# CHECK KEY
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['checkkey'])
def cmd_checkkey(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ *Cú pháp:* `/checkkey <key>`", parse_mode="Markdown")
        return
    check_and_reply(msg.chat.id, parts[1].strip().upper())

def check_and_reply(chat_id, key):
    db = load_db()
    if key not in db:
        bot.send_message(
            chat_id,
            f"❌ *KEY KHÔNG TỒN TẠI!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 Key: `{key}`\n"
            f"💡 Vui lòng kiểm tra lại.",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
        return
    info = db[key]
    if info["exp"] < time.time():
        exp_str = datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
        bot.send_message(
            chat_id,
            f"⌛ *KEY ĐÃ HẾT HẠN!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 Key: `{key}`\n"
            f"📅 Hết hạn: `{exp_str}`\n"
            f"💡 Vui lòng tạo key mới bằng `/newkey`",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )
    else:
        left = info["exp"] - time.time()
        d = int(left // 86400)
        h = int((left % 86400) // 3600)
        m = int((left % 3600) // 60)
        exp_str = datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
        bot.send_message(
            chat_id,
            f"✅ *KEY CÒN HOẠT ĐỘNG!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 Key: `{key}`\n"
            f"📅 Hết hạn: `{exp_str}`\n"
            f"⏳ Còn lại: *{d} ngày {h} giờ {m} phút*",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

# ═══════════════════════════════════════════════════════════
# LIST KEY
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['listkey'])
def cmd_listkey(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Không có quyền!")
        return
    send_list(msg.chat.id)

def send_list(chat_id):
    db = load_db()
    if not db:
        bot.send_message(chat_id, "📭 Chưa có key nào.", reply_markup=main_menu())
        return
    now = time.time()
    active = [(k, v) for k, v in db.items() if v["exp"] > now]
    expired = [(k, v) for k, v in db.items() if v["exp"] <= now]

    text = (
        f"📋 *DANH SÁCH KEY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Hoạt động: *{len(active)}*\n"
        f"⌛ Hết hạn: *{len(expired)}*\n"
        f"📊 Tổng: *{len(db)}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    if active:
        text += "*🟢 ĐANG HOẠT ĐỘNG:*\n"
        for k, v in active[:20]:
            exp_str = datetime.fromtimestamp(v["exp"]).strftime("%d/%m %H:%M")
            text += f"`{k}` — {exp_str}\n"
        if len(active) > 20:
            text += f"\n_...và {len(active)-20} key khác_"
    if len(text) > 4000:
        text = text[:3900] + "\n...(quá dài)"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())

# ═══════════════════════════════════════════════════════════
# DELETE KEY
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['delkey'])
def cmd_delkey(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Không có quyền!")
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ *Cú pháp:* `/delkey <key>`", parse_mode="Markdown")
        return
    key = parts[1].strip().upper()
    db = load_db()
    if key in db:
        del db[key]
        save_db(db)
        bot.reply_to(msg, f"🗑️ Đã xóa key `{key}`", parse_mode="Markdown", reply_markup=main_menu())
    else:
        bot.reply_to(msg, f"❌ Không tìm thấy key `{key}`", parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════
# MY ID
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['myid'])
def cmd_myid(msg):
    bot.reply_to(
        msg,
        f"🆔 *ID Telegram của bạn:*\n`{msg.from_user.id}`\n\n"
        f"💡 Copy ID này để cài làm ADMIN trong bot.",
        parse_mode="Markdown"
    )

# ═══════════════════════════════════════════════════════════
# CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    data = call.data
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if data == "menu":
        text = "🎮 *MENU CHÍNH*\n👇 Chọn chức năng:"
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu())
        except:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())

    elif data.startswith("quick_"):
        if not is_admin(user_id):
            bot.send_message(chat_id, "❌ Bạn không có quyền tạo key!")
            return
        days = int(data.split("_")[1])
        create_keys(chat_id, days, 1, user_id)

    elif data == "list_keys":
        if not is_admin(user_id):
            bot.send_message(chat_id, "❌ Không có quyền!")
            return
        send_list(chat_id)

    elif data == "stats":
        db = load_db()
        now = time.time()
        active = sum(1 for v in db.values() if v["exp"] > now)
        expired = len(db) - active
        text = (
            f"📊 *THỐNG KÊ HỆ THỐNG*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Key hoạt động: *{active}*\n"
            f"⌛ Key hết hạn: *{expired}*\n"
            f"📦 Tổng số key: *{len(db)}*\n"
            f"⏰ Cập nhật: `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`"
        )
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=back_button())
        except:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=back_button())

    elif data == "my_id":
        text = f"🆔 *ID của bạn:*\n`{user_id}`\n\n💡 Copy để cài ADMIN."
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=back_button())
        except:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=back_button())

    elif data == "help":
        text = (
            "❓ *TRỢ GIÚP*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔑 `/newkey <ngày> <số>`\n"
            "🔍 `/checkkey <key>`\n"
            "📋 `/listkey`\n"
            "🗑️ `/delkey <key>`\n"
            "🆔 `/myid`"
        )
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=back_button())
        except:
            bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=back_button())

# ═══════════════════════════════════════════════════════════
# HANDLE TEXT
# ═══════════════════════════════════════════════════════════
@bot.message_handler(func=lambda m: True)
def handle_text(msg):
    text = (msg.text or "").strip().upper()
    if text.startswith(("VIP-", "PRO-", "LUXURY-")):
        check_and_reply(msg.chat.id, text)
    else:
        bot.reply_to(msg, "💡 Gõ `/start` để mở menu!", parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════
# RUN BOT
# ═══════════════════════════════════════════════════════════
def run_bot():
    print("╔══════════════════════════════════════╗")
    print("║   🤖 BOT TELEGRAM ĐANG CHẠY...      ║")
    print("╚══════════════════════════════════════╝")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"⚠️ Bot lỗi: {e} — Thử lại sau 5s...")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
