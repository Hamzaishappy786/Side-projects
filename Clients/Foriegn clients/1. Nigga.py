from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


def read_credentials():
    """Read email and password from requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
            email = lines[0].strip()
            password = lines[1].strip()
            return email, password
    except Exception as e:
        print(f"Error reading credentials: {e}")
        return None, None


def wait_for_page_load(driver, timeout=10):
    """Wait for page to load completely"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        return True
    except TimeoutException:
        print("Page load timeout")
        return False


def main():
    # Read credentials
    email, password = read_credentials()
    if not email or not password:
        print("Failed to read credentials from requirements.txt")
        return

    print(f"Email: {email}")
    print("Password: ****")

    # Initialize Chrome driver
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        # Navigate to login page
        print("\n[1] Navigating to login page...")
        driver.get("https://auth.leadscampus.com/")

        # Wait for page to load completely
        wait_for_page_load(driver, timeout=10)
        time.sleep(3)  # Extra wait for any dynamic content

        # Try to find and switch to iframe if exists
        print("[2] Checking for iframes...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"   Found {len(iframes)} iframe(s), switching to first one...")
            driver.switch_to.frame(0)
            time.sleep(1)

        # Wait for email field and fill it
        print("[3] Waiting for email field...")
        try:
            email_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div/div/form/input[1]"))
            )
            print("[4] Entering email...")
            email_field.clear()
            email_field.send_keys(email)
        except Exception as e:
            print(f"   ✗ XPath failed, trying alternative selectors...")
            # Try alternative selectors
            try:
                email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                email_field.clear()
                email_field.send_keys(email)
            except:
                email_field = driver.find_element(By.NAME, "email")
                email_field.clear()
                email_field.send_keys(email)

        # Wait for password field and fill it
        print("[5] Entering password...")
        try:
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div/div/form/input[2]"))
            )
            password_field.clear()
            password_field.send_keys(password)
        except Exception as e:
            print(f"   ✗ XPath failed, trying alternative selectors...")
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                password_field.clear()
                password_field.send_keys(password)
            except:
                password_field = driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(password)

        # Click login button
        print("[6] Clicking login button...")
        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[2]/div/div/form/div[3]/input"))
            )
            login_button.click()
        except Exception as e:
            print(f"   ✗ XPath failed, trying alternative selectors...")
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                login_button.click()
            except:
                login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()

        # Switch back to default content if we were in iframe
        driver.switch_to.default_content()

        # Wait for page to load (4 seconds max, but check if loaded)
        print("[7] Waiting for login to complete...")
        time.sleep(2)
        if wait_for_page_load(driver, timeout=4):
            print("✓ Page loaded successfully")
        else:
            print("⚠ Page may not have loaded completely")
        time.sleep(2)  # Additional rest time

        # Navigate to SMS leads page
        print("\n[8] Navigating to SMS leads page...")
        driver.get("https://crm.leadscampus.com/smsleads.aspx")

        # Wait for SMS leads page to load
        wait_for_page_load(driver, timeout=10)
        time.sleep(2)
        print("✓ SMS leads page loaded successfully")

        # Click on the state dropdown
        print("\n[9] Opening state dropdown...")
        state_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "/html/body/form/div[3]/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div/span/span[1]/span"))
        )
        state_dropdown.click()
        time.sleep(1)
        print("✓ State dropdown opened")

        # Get the dropdown list container
        print("\n[10] Fetching states list...")
        states_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.select2-results__options"))
        )

        # Find all state items
        state_items = states_container.find_elements(By.TAG_NAME, "li")

        # Extract state names (skip the first "-- Select State --" option)
        state_names = []
        for idx, state in enumerate(state_items, 1):
            state_name = state.text.strip()
            if state_name and state_name != "-- Select State --":
                state_names.append(state_name)

        print(f"\n✓ Found {len(state_names)} states to download:")
        print("=" * 50)
        for idx, state_name in enumerate(state_names, 1):
            print(f"{idx}. {state_name}")
        print("=" * 50)

        # Close the dropdown first (click somewhere else)
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.5)

        # Now loop through each state and download
        print("\n[11] Starting download process...")
        for idx, state_name in enumerate(state_names, 1):
            try:
                print(f"\n[{idx}/{len(state_names)}] Processing: {state_name}")

                # Open dropdown
                state_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/form/div[3]/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div/span/span[1]/span"))
                )
                state_dropdown.click()
                time.sleep(0.5)

                # Find and click the specific state
                states_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.select2-results__options"))
                )

                # Find the state by text
                state_option = states_container.find_element(By.XPATH, f".//li[contains(text(), '{state_name}')]")
                state_option.click()
                time.sleep(1)  # Wait for page to update with selected state

                print(f"    ✓ Selected: {state_name}")
                print(f"    → Current URL: {driver.current_url}")

                # Click download button
                download_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/form/div[3]/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/a[1]"))
                )
                download_button.click()
                print(f"    ✓ Download initiated for {state_name}")

                # Wait before next iteration
                time.sleep(3)

            except Exception as e:
                print(f"    ✗ Error with {state_name}: {e}")
                continue

        print("\n" + "=" * 50)
        print("✓ All downloads completed successfully!")
        print(f"✓ Total states processed: {len(state_names)}")
        print("=" * 50)

        # Keep browser open for inspection
        input("\nPress Enter to close the browser...")

    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()

        # Debug: Save page source
        print("\n[DEBUG] Saving page source for inspection...")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✓ Page source saved to 'page_source.html'")

        # Keep browser open for manual inspection
        input("\nPress Enter to close the browser...")

    finally:
        driver.quit()
        print("\nBrowser closed.")


if __name__ == "__main__":
    main()