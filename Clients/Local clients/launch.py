import subprocess
import time
import requests
import os
import sys

# --- 🟢 YOUR CONFIGURATION (ALREADY FILLED) ---
APP_ID = "842649008366493"
APP_SECRET = "eba9dc8bd72da9acc31a3cd7a3351241"
VERIFY_TOKEN = "fb_token_786"
NGROK_PATH = "ngrok"  # Ensure ngrok.exe is in this folder

def get_ngrok_url():
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        return response.json()['tunnels'][0]['public_url']
    except:
        return None


def update_webhook(public_url, object_type, fields):
    webhook_url = f"{public_url}/webhook"
    params = {
        "object": object_type,
        "callback_url": webhook_url,
        "fields": fields,
        "verify_token": VERIFY_TOKEN,
        "access_token": f"{APP_ID}|{APP_SECRET}"
    }
    print(f"🔄 Updating {object_type} webhook to: {webhook_url}...")
    response = requests.post(f"https://graph.facebook.com/{APP_ID}/subscriptions", params=params)
    if "success" in response.text:
        print(f"✅ {object_type} updated SUCCESSFULLY.")
    else:
        print(f"❌ FAILED {object_type}: {response.text}")


def main():
    print("🚀 STARTING CLIENT PRODUCT SYSTEM...")

    # 1. Start Bot
    print("🔹 Starting AI Bot Server...")
    # This runs 'main.py' in a separate window
    bot_process = subprocess.Popen([sys.executable, "main.py"], cwd=os.getcwd(),
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(3)

    # 2. Start Ngrok
    print("🔹 Starting Tunnel (Ngrok)...")
    ngrok_process = subprocess.Popen([NGROK_PATH, "http", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)

    # 3. Get URL & Update Facebook
    url = get_ngrok_url()
    if url:
        print(f"🌍 SYSTEM LIVE AT: {url}")
        update_webhook(url, "page", "leadgen")
        update_webhook(url, "whatsapp_business_account", "messages")
        print("\n✨ SYSTEM READY. MINIMIZE THIS WINDOW.")

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            bot_process.terminate()
            ngrok_process.terminate()
    else:
        print("❌ Ngrok failed to start.")
        bot_process.terminate()


if __name__ == "__main__":
    main()