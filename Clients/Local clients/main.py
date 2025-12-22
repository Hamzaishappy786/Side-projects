from fastapi import FastAPI, Request, HTTPException
import uvicorn
import requests

app = FastAPI()

# --- 🟢 YOUR CONFIGURATION (ALREADY FILLED) ---
VERIFY_TOKEN = "fb_token_786"
PAGE_ACCESS_TOKEN = "EAALZBYoLQY50BQOlmIMUEmh8gy6ke1zW0VEyxTU776ZB5ZBcDfUxZAyA4Lzat0dnU6wOWywZClqCKg5AqP7eyJ2l6C2GvWUQcchjTURkbiAe9tlpRLY4BJZCRExlDymPuS81dB60qxu2WXvsfsUYfWZC9pxvfwej4xeZCHZAJkqrVJSZAaIJsi2wAtdVDR1PmZCdUjDHbXyA5ECi8x8qv2wu7O6YWhS9J7hc0VTmuZAqAjwIBQVFjdJVB3BaRceBtQZA1I0B0Tr6pHvAGnIYSYichUd0akNX5rgZDZD"
WHATSAPP_TOKEN = "EAALZBYoLQY50BQNS0fkuKqhAzS53GqtVgwZASHCPqH2csZCqgHON37rBUSi0HF6zPaj9MqqzOqvlLZA1qaia2b5dR85EUPOAm7jPpAMqT85GeZCakBY4ap92UZB9niw6NElmGP6r8M3NyXngz6w463CzkqVJiDeYCk3ZCZA5yZAeAHxkBI4w0xYdWgZBGbIcIlL6SETkSBsk0s3vNFZANs7E13AQkcEToE9WiqRfMSWZBaq3r8BDd8jRE5xYR129QEfdeGKBolU3iOvoIsawWTdIhMzgkkBbxQZDZD"
PHONE_NUMBER_ID = "847122261826117"
GEMINI_API_KEY = "AIzaSyDIbwnA_HQAZTEgSxS0oZ5oi0elHeXRzZg"

# --- 🟢 ASSETS ---
BROCHURE_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
CALENDAR_LINK = "https://calendly.com/"


# --- 🧠 BRAIN (DIRECT API CALL) ---
def ask_gemini_direct(user_message):
    # Using 'gemini-2.0-flash' which is active on your key
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    system_instruction = """
    You are 'Sarah', a Senior Consultant for Prestige Developments.

    LOGIC RULES:
    1. If the user asks for photos, floor plans, or brochure:
       - Explain briefly what is in it.
       - End your message EXACTLY with: [SEND_BROCHURE]

    2. If the user seems interested, asks about price, or ROI:
       - Give the info, then suggest a brief call.
       - If they say "Yes" or ask to book:
       - End your message EXACTLY with: [SEND_BOOKING]

    3. Otherwise, just answer politely and keep it under 50 words.
    """

    payload = {
        "contents": [{
            "parts": [{"text": f"{system_instruction}\n\nUser Question: {user_message}"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ Gemini Error: {response.text}")
            return "I am checking that detail for you."
    except Exception as e:
        print(f"Connection Error: {e}")
        return "I'll be with you in a moment."


# --- 📨 WHATSAPP FUNCTIONS ---
def send_text(to_number, text):
    clean_text = text.replace("[SEND_BROCHURE]", "").replace("[SEND_BOOKING]", "").strip()
    if not clean_text: return

    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": clean_text}
    }
    requests.post(url, headers=headers, json=payload)


def send_pdf(to_number):
    print(f"📂 SENDING PDF TO {to_number}...")
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp", "to": to_number, "type": "document",
        "document": {"link": BROCHURE_URL, "filename": "Prestige_Brochure.pdf",
                     "caption": "Here are the floor plans. 📄"}
    }
    requests.post(url, headers=headers, json=payload)


def send_booking_link(to_number):
    print(f"📅 SENDING CALENDAR TO {to_number}...")
    send_text(to_number, f"Please select a time here: {CALENDAR_LINK}")


# --- 🔗 WEBHOOKS ---
@app.get("/webhook")
async def verify_webhook(request: Request):
    if request.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(request.query_params.get("hub.challenge"))
    raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook")
async def receive_data(request: Request):
    data = await request.json()
    try:
        if 'messages' in str(data):
            entry = data['entry'][0]['changes'][0]['value']
            if 'messages' in entry:
                msg = entry['messages'][0]
                sender = msg['from']
                text = msg['text']['body']
                print(f"💬 USER ({sender}): {text}")

                ai_reply = ask_gemini_direct(text)
                print(f"🤖 AI: {ai_reply}")

                send_text(sender, ai_reply)

                if "[SEND_BROCHURE]" in ai_reply: send_pdf(sender)
                if "[SEND_BOOKING]" in ai_reply: send_booking_link(sender)

    except Exception as e:
        print(f"Log: {e}")
    return {"status": "received"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)