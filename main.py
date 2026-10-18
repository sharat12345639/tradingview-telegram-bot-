import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Fetch credentials securely from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

@app.route('/', methods=['GET'])
def health_check():
    return "RSI Alert Server is Live 24/7!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload"}), 400

    event  = data.get("event")
    tf     = data.get("tf", "4H")
    symbol = data.get("symbol", "UNKNOWN")
    price  = data.get("price", "N/A")
    rsi    = data.get("rsi", "N/A")

    if event == "RSI_OB_UP":
        msg = f"🔴 <b>[{tf}] RSI OVERBOUGHT CROSS UP</b>\n\n<b>Symbol:</b> {symbol}\n<b>Price:</b> {price}\n<b>RSI:</b> {rsi} (Crossed ABOVE 70)"
    elif event == "RSI_OB_DOWN":
        msg = f"🟠 <b>[{tf}] RSI OVERBOUGHT CROSS DOWN</b>\n\n<b>Symbol:</b> {symbol}\n<b>Price:</b> {price}\n<b>RSI:</b> {rsi} (Crossed BELOW 70)"
    elif event == "RSI_OS_UP":
        msg = f"🟢 <b>[{tf}] RSI OVERSOLD CROSS UP</b>\n\n<b>Symbol:</b> {symbol}\n<b>Price:</b> {price}\n<b>RSI:</b> {rsi} (Crossed ABOVE 30)"
    elif event == "RSI_OS_DOWN":
        msg = f"🟢 <b>[{tf}] RSI OVERSOLD CROSS DOWN</b>\n\n<b>Symbol:</b> {symbol}\n<b>Price:</b> {price}\n<b>RSI:</b> {rsi} (Crossed BELOW 30)"
    else:
        msg = f"🔔 <b>[{tf}] RSI ALERT TRIGGERED</b>\n\n{data}"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}

    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
