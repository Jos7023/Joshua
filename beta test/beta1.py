from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

def log_time(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

try:
    log_time("Setting up WebDriver...")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment this to run without opening the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
except Exception as e:
    log_time(f"Error initializing WebDriver: {e}")
    exit(1)

# URL to monitor
url = "https://odibets.com/odileague"

# To keep track of the last seen class names
last_class_names = []

try:
    log_time("Starting 2-minute monitoring loop...")
    while True:
        log_time("Opening OdiLeague URL...")
        driver.get(url)

        # Wait for page to load and for the ss elements to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ss"))
        )

        ss_elements = driver.find_elements(By.CLASS_NAME, "ss")

        if ss_elements:
            log_time(f"Found {len(ss_elements)} ss elements.")
            current_class_names = []

            for index, element in enumerate(ss_elements, start=1):
                element_text = element.text.strip()
                class_names = element.get_attribute("class").strip()
                current_class_names.append(class_names)

                log_time(f"Element {index}: Text: {element_text}, Class Names: {class_names}")

            # Compare with previous
            if last_class_names and current_class_names != last_class_names:
                log_time("⚠️ Class names have changed since the last check.")
            else:
                log_time("✅ No change in class names.")

            # Update last seen class names
            last_class_names = current_class_names
        else:
            log_time("No ss elements found.")

        log_time("Waiting 2 minutes before next check...\n")
        time.sleep(120)  # Wait 2 minutes

except KeyboardInterrupt:
    log_time("Monitoring stopped by user.")
except Exception as e:
    log_time(f"Error during execution: {e}")
finally:
    driver.quit()
    log_time("Driver closed.")
