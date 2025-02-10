import requests
import json
from flask import Flask, request

app = Flask(__name__)

# Ganti dengan data dari WhatsApp Cloud API
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"  # Masukkan Access Token dari Meta
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"  # Masukkan Phone Number ID dari Meta
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"  # Token untuk verifikasi webhook

# Daftar kata yang akan difilter
BLOCKED_WORDS = ["kata1", "kata2", "kata3"]

def send_whatsapp_message(to, message):
    """Mengirim pesan WhatsApp melalui Cloud API."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook untuk menerima pesan WhatsApp dan meresponsnya."""
    if request.method == 'GET':
        # Untuk verifikasi webhook di Facebook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge
        else:
            return "Verification failed", 403

    elif request.method == 'POST':
        data = request.get_json()
        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "messages" in change["value"]:
                        message_data = change["value"]["messages"][0]
                        from_number = message_data["from"]  # Nomor pengirim
                        message_text = message_data["text"]["body"]  # Isi pesan

                        # Cek apakah pesan mengandung kata yang dilarang
                        if any(word in message_text.lower() for word in BLOCKED_WORDS):
                            response_text = "⚠️ Pesan ini mengandung kata yang tidak diperbolehkan!"
                        else:
                            response_text = f"✅ Pesan diterima: {message_text}"

                        # Kirim respons ke pengirim
                        send_whatsapp_message(from_number, response_text)

        return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

