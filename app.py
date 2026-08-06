from flask import Flask, request
import os

app = Flask(__name__)

VERIFY_TOKEN = "Khuzaifa_verify_2026"

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI Assistant is running!"

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)