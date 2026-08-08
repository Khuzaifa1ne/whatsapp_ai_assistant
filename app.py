from flask import Flask, request
import os
import requests
from openai import OpenAI

app = Flask(__name__)

# =========================
# ENVIRONMENT VARIABLES
# =========================

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# =========================
# HOME
# =========================

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI Assistant is running!"


# =========================
# META WEBHOOK VERIFICATION
# =========================

@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "Verification failed", 403


# =========================
# RECEIVE WHATSAPP MESSAGE
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    print("Incoming WhatsApp message:")
    print(data)

    try:

        # Get the WhatsApp message
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        # Only process text messages
        if message.get("type") != "text":
            return "EVENT_RECEIVED", 200

        # Customer's WhatsApp number
        sender = message["from"]

        # Customer's message
        user_message = message["text"]["body"]

        print("Customer:", sender)
        print("Message:", user_message)

        # =========================
        # ASK OPENAI
        # =========================

        response = client.responses.create(
            model="gpt-5",
            instructions="""
You are Khuzaifa AI Assistant, a helpful WhatsApp business assistant.

Be friendly, professional and concise.

If a customer asks about the business and you don't have enough information,
ask them a simple follow-up question instead of inventing information.
""",
            input=user_message
        )

        ai_reply = response.output_text

        print("AI reply:", ai_reply)

        # =========================
        # SEND REPLY TO WHATSAPP
        # =========================

        url = f"https://graph.facebook.com/v26.0/{PHONE_NUMBER_ID}/messages"

        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": sender,
            "type": "text",
            "text": {
                "body": ai_reply
            }
        }

        whatsapp_response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        print("WhatsApp response:")
        print(whatsapp_response.status_code)
        print(whatsapp_response.text)

    except Exception as e:

        print("ERROR:", str(e))

    return "EVENT_RECEIVED", 200


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )