# ═══════════════════════════════════════════════════════════
# 🌐 SERVER FLASK API — FULL FIX
# ═══════════════════════════════════════════════════════════
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder=".")

# ⚠️ CORS: Cho phép MỌI domain gọi API (kể cả web riêng của bạn)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.json")

# ═══════════════════════════════════════════════════════════
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# ═══════════════════════════════════════════════════════════
# API: CHECK KEY
# ═══════════════════════════════════════════════════════════
@app.route("/api/check", methods=["POST", "OPTIONS"])
def api_check():
    # Xử lý preflight CORS
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json() or {}
    key = (data.get("key") or "").strip().upper()

    if not key:
        return jsonify({"status": "invalid", "message": "Chưa nhập key"})

    db = load_db()
    if key not in db:
        return jsonify({"status": "invalid", "message": "Key không tồn tại"})

    info = db[key]
    now = time.time()

    if info["exp"] < now:
        return jsonify({
            "status": "expired",
            "message": "Key đã hết hạn",
            "expired_at": datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
        })

    left = info["exp"] - now
    return jsonify({
        "status": "active",
        "message": "Key hợp lệ",
        "days": info.get("days", 0),
        "exp": info["exp"],
        "left_seconds": int(left),
        "expired_at": datetime.fromtimestamp(info["exp"]).strftime("%d/%m/%Y %H:%M")
    })

# ═══════════════════════════════════════════════════════════
# API: INFO
# ═══════════════════════════════════════════════════════════
@app.route("/api/info", methods=["GET"])
def api_info():
    db = load_db()
    now = time.time()
    active = sum(1 for v in db.values() if v["exp"] > now)
    return jsonify({
        "status": "ok",
        "total": len(db),
        "active": active,
        "expired": len(db) - active,
        "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

# ═══════════════════════════════════════════════════════════
# HEALTH CHECK (cho Render/UptimeRobot)
# ═══════════════════════════════════════════════════════════
@app.route("/healthz")
def health():
    return "OK", 200

# ═══════════════════════════════════════════════════════════
# ROOT: SERVE HTML nếu có
# ═══════════════════════════════════════════════════════════
@app.route("/")
def index():
    if os.path.exists("index.html"):
        return send_from_directory(".", "index.html")
    return jsonify({
        "status": "ok",
        "message": "API Game Tool đang chạy",
        "endpoints": ["/api/check", "/api/info", "/healthz"]
    })

# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 API đang chạy tại: http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
