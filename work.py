from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pyautogui
import time
from PIL import Image
import io
import os
import subprocess

# Configuration
URL = "https://hailuoai.video/create/image-generation"
IMAGE_PATH = "client ka kaam.png"
XPATH = "/html/body/main/div/section/section/main/section/div/div[1]/div/div[2]/div/div/div/div[4]/div/div/div/div/div[1]/div[2]/div/div/p"


def is_chrome_running():
    """Check if Chrome is running"""
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        return 'chrome.exe' in result.stdout.lower()
    except:
        return False


def start_chrome_with_debugging():
    """Start Chrome with remote debugging if not already running"""
    if not is_chrome_running():
        print("Chrome not running. Please open Chrome first!")
        return False

    # Check if debugging port is available
    try:
        import requests
        response = requests.get("http://localhost:9222/json/version", timeout=2)
        if response.status_code == 200:
            print("✓ Chrome is running with debugging enabled")
            return True
    except:
        pass

    print("\n" + "=" * 60)
    print("Chrome is running but debugging is not enabled.")
    print("Please close Chrome and run this command:")
    print('chrome.exe --remote-debugging-port=9222')
    print("\nOR just keep Chrome open and the bot will try to work anyway...")
    print("=" * 60)
    return True


def copy_image_to_clipboard(image_path):
    """Copy image to clipboard"""
    try:
        abs_path = os.path.abspath(image_path)
        if not os.path.exists(abs_path):
            print(f"✗ Error: Image file not found at {abs_path}")
            return False

        # Use PowerShell to copy image
        ps_command = f'[System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile("{abs_path}"))'
        full_command = f'powershell -command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; {ps_command}"'

        os.system(full_command)
        print(f"✓ Image copied to clipboard")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"✗ Error copying image: {e}")
        return False


def run_bot():
    """Main bot function"""
    driver = None

    try:
        print("Starting bot...")
        print("=" * 60)

        # Check if image exists
        if not os.path.exists(IMAGE_PATH):
            print(f"✗ ERROR: Image file '{IMAGE_PATH}' not found!")
            return

        # Check if Chrome is running
        if not is_chrome_running():
            print("✗ ERROR: Chrome is not running!")
            print("Please open Chrome first, then run this bot.")
            return

        print("✓ Chrome is running")

        # Try to connect to Chrome with debugging
        print("\nConnecting to Chrome...")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("✓ Connected to existing Chrome session")
        except Exception as e:
            print(f"✗ Could not connect to Chrome with debugging: {e}")
            print("\nTo fix this, close Chrome and start it with:")
            print("chrome.exe --remote-debugging-port=9222")
            return

        # Navigate to URL
        print(f"\nNavigating to: {URL}")
        driver.get(URL)
        print("✓ Page loading...")

        # Wait for page to load
        time.sleep(8)
        print(f"✓ Current URL: {driver.current_url}")

        # Copy image to clipboard
        print(f"\nCopying image: {IMAGE_PATH}")
        if not copy_image_to_clipboard(IMAGE_PATH):
            print("✗ Failed to copy image")
            return

        # Find the paste area
        print(f"\nLooking for paste area...")
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.presence_of_element_located((By.XPATH, XPATH)))
        print("✓ Found paste area element")

        # Scroll to element
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)

        # Click element
        print("\nClicking paste area...")
        element.click()
        print("✓ Clicked")
        time.sleep(2)

        # Paste image
        print("\nPasting image (Ctrl+V)...")
        pyautogui.hotkey('ctrl', 'v')
        print("✓ Paste command sent")

        print("=" * 60)
        print("✓ BOT COMPLETED!")
        print("=" * 60)

        # Wait to see result
        time.sleep(10)

    except Exception as e:
        print("=" * 60)
        print(f"✗ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()

    finally:
        print("\nChrome will remain open with your session.")


if __name__ == "__main__":
    # Check if Chrome is running first
    if not is_chrome_running():
        print("=" * 60)
        print("PLEASE OPEN CHROME FIRST!")
        print("=" * 60)
        print("\nFor best results, start Chrome with debugging:")
        print('chrome.exe --remote-debugging-port=9222')
        print("\nThen run this bot again.")
        print("=" * 60)
    else:
        run_bot()