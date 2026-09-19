# ═══════════════════════════════════════════════════════════
# 🎮 GAME TOOL — BOT + API + MOBILECONFIG
# ═══════════════════════════════════════════════════════════
import telebot
from telebot import types
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time, random, string, json, os, threading, io, uuid
from datetime import datetime, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8081809059:AAEV5cUJJ660gpKdLTlMta22Ary5pnRxy4Q")
ADMIN_IDS = []
DB_FILE = "keys.json"
PORT = int(os.environ.get("PORT", 5000))
WEB_URL = os.environ.get("WEB_URL", "https://game-tool.vercel.app")  # đổi thành link web của bạn

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
_lock = threading.Lock()

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════
def load_db():
    with _lock:
        if not os.path.exists(DB_FILE): return {}
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}

def save_db(db):
    with _lock:
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
        except Exception as e: print(f"⚠️ {e}")

def is_admin(uid): return len(ADMIN_IDS) == 0 or uid in ADMIN_IDS

def gen_key(prefix="VIP"):
    return f"{prefix}-{''.join(random.choices(string.ascii_uppercase+string.digits, k=10))}"

# ═══════════════════════════════════════════════════════════
# TẠO FILE .mobileconfig
# ═══════════════════════════════════════════════════════════
def build_mobileconfig(key, days, exp_time, phone="iPhone"):
    uuid1 = str(uuid.uuid4()).upper()
    uuid2 = str(uuid.uuid4()).upper()
    exp_str = datetime.fromtimestamp(exp_time).strftime("%d/%m/%Y %H:%M")

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadDescription</key>
            <string>Cấu hình CÔNG CỤ HỖ TRỢ GAME</string>
            <key>PayloadDisplayName</key>
            <string>Key: {key}</string>
            <key>PayloadIdentifier</key>
            <string>com.gametool.config.{uuid1}</string>
            <key>PayloadOrganization</key>
            <string>CÔNG CỤ HỖ TRỢ GAME</string>
            <key>PayloadType</key>
            <string>com.apple.applicationaccess</string>
            <key>PayloadUUID</key>
            <string>{uuid1}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>PayloadContent</key>
            <dict>
                <key>allowCamera</key>
                <true/>
                <key>allowScreenShot</key>
                <true/>
                <key>ratingRegion</key>
                <string>vn</string>
            </dict>
        </dict>
        <dict>
            <key>PayloadDescription</key>
            <string>Tạo icon GAME TOOL trên màn hình chính</string>
            <key>PayloadDisplayName</key>
            <string>GAME TOOL</string>
            <key>PayloadIdentifier</key>
            <string>com.gametool.webclip.{uuid2}</string>
            <key>PayloadOrganization</key>
            <string>CÔNG CỤ HỖ TRỢ GAME</string>
            <key>PayloadType</key>
            <string>com.apple.webClip.managed</string>
            <key>PayloadUUID</key>
            <string>{uuid2}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>URL</key>
            <string>{WEB_URL}</string>
            <key>Label</key>
            <string>GAME TOOL</string>
            <key>IsRemovable</key>
            <true/>
            <key>Precomposed</key>
            <true/>
        </dict>
    </array>
    <key>PayloadDescription</key>
    <string>Key: {key} | Hạn: {days} ngày | Hết hạn: {exp_str} | Thiết bị: {phone}</string>
    <key>PayloadDisplayName</key>
    <string>Game Tool - {phone}</string>
    <key>PayloadIdentifier</key>
    <string>com.gametool.profile.{uuid1}</string>
    <key>PayloadOrganization</key>
    <string>CÔNG CỤ HỖ TRỢ GAME</string>
    <key>PayloadRemovalDisallowed</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{uuid1}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
    <key>ConsentText</key>
    <dict>
        <key>default</key>
        <string>CÔNG CỤ HỖ TRỢ GAME
Key: {key}
Hạn: {days} ngày
Hết hạn: {exp_str}
Thiết bị: {phone}</string>
    </dict>
</dict>
</plist>'''

# ═══════════════════════════════════════════════════════════
# MENU BOT
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
        types.InlineKeyboardButton("📋 Danh Sách", callback_data="list_keys"),
        types.InlineKeyboardButton("📊 Thống Kê", callback_data="stats"),
    )
    kb.add(
        types.InlineKeyboardButton("🆔 ID", callback_data="my_id"),
        types.InlineKeyboardButton("❓ Trợ Giúp", callback_data="help"),
    )
    return kb

def back_button():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Menu", callback_data="menu"))
    return kb

@bot.message_handler(commands=['start'])
def cmd_start(msg):
    name = msg.from_user.first_name or "bạn"
    text = (
        f"🎮 *CÔNG CỤ HỖ TRỢ GAME*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 Chào *{name}*!\n\n"
        f"🔑 `/newkey <ngày> <số>` — Tạo key\n"
        f"🔍 `/checkkey <key>` — Kiểm tra\n"
        f"🍎 `/getconfig <key>` — Tải file .mobileconfig\n"
        f"📋 `/listkey` — Danh sách\n"
        f"🗑️ `/delkey <key>` — Xóa\n"
        f"🆔 `/myid` — Lấy ID\n\n"
        f"💡 *Bấm nút bên dưới để tạo nhanh!*"
    )
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def cmd_help(msg):
    bot.send_message(msg.chat.id,
        "❓ *TRỢ GIÚP*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔑 `/newkey 7 3` → 3 key hạn 7 ngày\n"
        "🔍 `/checkkey VIP-ABC123` → kiểm tra\n"
        "🍎 `/getconfig VIP-ABC123` → tải .mobileconfig\n"
        "📋 `/listkey` → xem tất cả\n"
        "🗑️ `/delkey VIP-ABC123` → xóa\n"
        "🆔 `/myid` → lấy ID",
        parse_mode="Markdown", reply_markup=back_button())

# ═══════════════════════════════════════════════════════════
# TẠO KEY
# ═══════════════════════════════════════════════════════════
def create_keys(chat_id, days, qty, user_id):
    db = load_db()
    exp_time = time.time() + days * 86400
    exp_str = (datetime.now() + timedelta(days=days)).strftime("%d/%m/%Y %H:%M")
    keys = []
    for _ in range(qty):
        prefix = "PRO" if days < 7 else ("LUXURY" if days >= 365 else "VIP")
        k = gen_key(prefix)
        while k in db: k = gen_key(prefix)
        db[k] = {"exp": exp_time, "days": days, "created": time.time(), "created_by": user_id}
        keys.append(k)
    save_db(db)
    text = (
        f"✅ *TẠO KEY THÀNH CÔNG!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 {qty} key — ⏰ {days} ngày\n"
        f"📅 Hết hạn: `{exp_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for k in keys: text += f"🔑 `{k}`\n"
    text += "\n💡 *Copy key → nhập web*\n🍎 */getconfig <key>* → tải .mobileconfig"
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['newkey'])
def cmd_newkey(msg):
    if not is_admin(msg.from_user.id): bot.reply_to(msg, "❌ Không có quyền!"); return
    try:
        parts = msg.text.split()
        days = max(1, min(int(parts[1]) if len(parts) > 1 else 7, 3650))
        qty = max(1, min(int(parts[2]) if len(parts) > 2 else 1, 50))
    except: bot.reply_to(msg, "⚠️ `/newkey <ngày> <số>`", parse_mode="Markdown"); return
    create_keys(msg.chat.id, days, qty, msg.from_user.id)

# ═══════════════════════════════════════════════════════════
# CHECK KEY
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['checkkey'])
def cmd_checkkey(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2: bot.reply_to(msg, "⚠️ `/checkkey <key>`", parse_mode="Markdown"); return
    check_and_reply(msg.chat.id, parts[1].strip().upper())

def check_and_reply(chat_id, key):
    db = load_db()
    if key not in db:
        bot.send_message(chat_id, f"❌ Key `{key}` không tồn tại!", parse_mode="Markdown", reply_markup=main_menu()); return
    info = db[key]
    if info["exp"] < time.time():
        exp = datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
        bot.send_message(chat_id, f"⌛ Key `{key}` *ĐÃ HẾT HẠN!*\n📅 `{exp}`", parse_mode="Markdown", reply_markup=main_menu())
    else:
        left = info["exp"] - time.time()
        d = int(left//86400); h = int((left%86400)//3600); m = int((left%3600)//60)
        exp = datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
        bot.send_message(chat_id, f"✅ Key `{key}` *CÒN HOẠT ĐỘNG*\n📅 `{exp}`\n⏳ *{d}n {h}h {m}p*", parse_mode="Markdown", reply_markup=main_menu())

# ═══════════════════════════════════════════════════════════
# LỆNH /getconfig — GỬI FILE .mobileconfig
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['getconfig'])
def cmd_getconfig(msg):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ *Cú pháp:* `/getconfig <key>`\n📌 VD: `/getconfig VIP-ABC123`", parse_mode="Markdown")
        return
    key = parts[1].strip().upper()
    db = load_db()

    if key not in db:
        bot.reply_to(msg, f"❌ Key `{key}` không tồn tại!", parse_mode="Markdown")
        return

    info = db[key]
    if info["exp"] < time.time():
        exp = datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
        bot.reply_to(msg, f"⌛ Key `{key}` *ĐÃ HẾT HẠN!*\n📅 `{exp}`", parse_mode="Markdown")
        return

    # Tạo file .mobileconfig
    config_content = build_mobileconfig(key, info["days"], info["exp"])
    config_bytes = io.BytesIO(config_content.encode("utf-8"))
    config_bytes.name = f"GameTool_{key}.mobileconfig"

    exp_str = datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
    left = info["exp"] - time.time()
    d = int(left//86400); h = int((left%86400)//3600)

    bot.send_document(
        msg.chat.id,
        config_bytes,
        caption=(
            f"🍎 *FILE CẤU HÌNH .mobileconfig*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 Key: `{key}`\n"
            f"⏰ Hạn: *{info['days']} ngày*\n"
            f"📅 Hết hạn: `{exp_str}`\n"
            f"⏳ Còn: *{d}n {h}h*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📱 *HƯỚNG DẪN CÀI TRÊN IPHONE:*\n"
            f"1️⃣ Tải file về iPhone\n"
            f"2️⃣ Mở file → iOS hỏi cài Profile → *Cho phép*\n"
            f"3️⃣ Vào *Cài đặt → Cài đặt chung → VPN & Thiết bị*\n"
            f"4️⃣ Bấm Profile → *Cài đặt* → Nhập mật khẩu → *Cài*\n"
            f"5️⃣ Xong! Icon GAME TOOL xuất hiện ✅"
        ),
        parse_mode="Markdown"
    )

# ═══════════════════════════════════════════════════════════
# LIST / DELETE / MYID
# ═══════════════════════════════════════════════════════════
@bot.message_handler(commands=['listkey'])
def cmd_listkey(msg):
    if not is_admin(msg.from_user.id): bot.reply_to(msg, "❌ Không có quyền!"); return
    db = load_db()
    if not db: bot.send_message(msg.chat.id, "📭 Chưa có key.", reply_markup=main_menu()); return
    now = time.time()
    active = [(k,v) for k,v in db.items() if v["exp"] > now]
    expired = [(k,v) for k,v in db.items() if v["exp"] <= now]
    text = f"📋 *DANH SÁCH KEY*\n✅ {len(active)} hoạt động\n⌛ {len(expired)} hết hạn\n📊 Tổng: {len(db)}\n\n"
    for k,v in active[:20]:
        text += f"`{k}` — {datetime.fromtimestamp(v['exp']).strftime('%d/%m %H:%M')}\n"
    if len(text) > 4000: text = text[:3900] + "\n..."
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(commands=['delkey'])
def cmd_delkey(msg):
    if not is_admin(msg.from_user.id): bot.reply_to(msg, "❌ Không có quyền!"); return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2: bot.reply_to(msg, "⚠️ `/delkey <key>`", parse_mode="Markdown"); return
    key = parts[1].strip().upper()
    db = load_db()
    if key in db:
        del db[key]; save_db(db)
        bot.reply_to(msg, f"🗑️ Đã xóa `{key}`", parse_mode="Markdown")
    else: bot.reply_to(msg, f"❌ Không tìm thấy `{key}`", parse_mode="Markdown")

@bot.message_handler(commands=['myid'])
def cmd_myid(msg): bot.reply_to(msg, f"🆔 `{msg.from_user.id}`", parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════
# CALLBACK
# ═══════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    data = call.data; chat_id = call.message.chat.id; user_id = call.from_user.id
    try: bot.answer_callback_query(call.id)
    except: pass

    if data == "menu":
        try: bot.edit_message_text("🎮 *MENU*", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu())
        except: bot.send_message(chat_id, "🎮 *MENU*", parse_mode="Markdown", reply_markup=main_menu())

    elif data.startswith("quick_"):
        if not is_admin(user_id): bot.send_message(chat_id, "❌ Không có quyền!"); return
        create_keys(chat_id, int(data.split("_")[1]), 1, user_id)

    elif data == "list_keys":
        if not is_admin(user_id): bot.send_message(chat_id, "❌ Không có quyền!"); return
        cmd_listkey(call.message)

    elif data == "stats":
        db = load_db(); now = time.time()
        active = sum(1 for v in db.values() if v["exp"] > now)
        text = f"📊 *THỐNG KÊ*\n✅ {active} hoạt động\n⌛ {len(db)-active} hết hạn\n📦 Tổng: {len(db)}"
        try: bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=back_button())
        except: bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=back_button())

    elif data == "my_id":
        text = f"🆔 `{user_id}`"
        try: bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=back_button())
        except: bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=back_button())

    elif data == "help":
        text = (
            "❓ *TRỢ GIÚP*\n"
            "🔑 `/newkey <ngày> <số>`\n"
            "🔍 `/checkkey <key>`\n"
            "🍎 `/getconfig <key>` → file .mobileconfig\n"
            "📋 `/listkey`\n"
            "🗑️ `/delkey <key>`\n"
            "🆔 `/myid`"
        )
        try: bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=back_button())
        except: bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=back_button())

@bot.message_handler(func=lambda m: True)
def handle_text(msg):
    text = (msg.text or "").strip().upper()
    if text.startswith(("VIP-", "PRO-", "LUXURY-")): check_and_reply(msg.chat.id, text)
    else: bot.reply_to(msg, "💡 Gõ `/start`!", parse_mode="Markdown")

# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════
@app.route("/api/check", methods=["POST", "OPTIONS"])
def api_check():
    if request.method == "OPTIONS": return "", 200
    data = request.get_json() or {}
    key = (data.get("key") or "").strip().upper()
    if not key: return jsonify({"status": "invalid", "message": "Chưa nhập key"})
    db = load_db()
    if key not in db: return jsonify({"status": "invalid", "message": "Key không tồn tại"})
    info = db[key]; now = time.time()
    if info["exp"] < now:
        return jsonify({"status": "expired", "message": "Key đã hết hạn",
                        "expired_at": datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")})
    return jsonify({"status": "active", "message": "Key hợp lệ", "days": info.get("days", 0),
                    "exp": info["exp"], "left_seconds": int(info["exp"] - now),
                    "expired_at": datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")})

# ═══ API: TẢI FILE .mobileconfig TỪ WEB ═══
@app.route("/api/mobileconfig", methods=["POST", "OPTIONS"])
def api_mobileconfig():
    if request.method == "OPTIONS": return "", 200
    data = request.get_json() or {}
    key = (data.get("key") or "").strip().upper()
    phone = (data.get("phone") or "iPhone").strip()

    if not key: return jsonify({"status": "invalid", "message": "Chưa có key"}), 400
    db = load_db()
    if key not in db: return jsonify({"status": "invalid", "message": "Key không tồn tại"}), 404
    info = db[key]
    if info["exp"] < time.time():
        return jsonify({"status": "expired", "message": "Key đã hết hạn"}), 403

    # Tạo file
    config_content = build_mobileconfig(key, info["days"], info["exp"], phone)
    config_bytes = io.BytesIO(config_content.encode("utf-8"))
    config_bytes.name = f"GameTool_{key}.mobileconfig"

    return send_file(
        config_bytes,
        mimetype="application/x-apple-aspen-config",
        as_attachment=True,
        download_name=f"GameTool_{key}.mobileconfig"
    )

@app.route("/api/info")
def api_info():
    db = load_db(); now = time.time()
    active = sum(1 for v in db.values() if v["exp"] > now)
    return jsonify({"status": "ok", "total": len(db), "active": active, "expired": len(db)-active})

@app.route("/healthz")
def health(): return "OK", 200

@app.route("/")
def root():
    return jsonify({"status": "ok", "message": "API + Bot đang chạy", "web": WEB_URL})

# ═══════════════════════════════════════════════════════════
# START BOT
# ═══════════════════════════════════════════════════════════
def run_bot():
    print("🤖 Bot đang chạy...")
    while True:
        try: bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"⚠️ Bot lỗi: {e}"); time.sleep(5)

_bot_started = False
def start_bot():
    global _bot_started
    if _bot_started: return
    _bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
    print("✅ Bot thread OK")

start_bot()

if __name__ == "__main__":
    print(f"🌐 API: http://0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
