from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import re

def log_time(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

def save_ss_texts(ss_elements, filename="ss_texts.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        for idx, element in enumerate(ss_elements, 1):
            text = element.text.strip()
            log_time(f"ss element {idx} text: {text}")
            f.write(f"{text}\n")

def track_countdown_timer(element, countdown_pattern):
    """Tracks the countdown timer in the given element until it reaches 00:10 or disappears.
    Returns True if it reaches 00:10, else False."""
    match = countdown_pattern.search(element.text)
    if match:
        countdown_value = match.group()
        log_time(f"Countdown timer found in first ss element: {countdown_value}")
        prev_value = countdown_value
        while True:
            try:
                current_text = element.text.strip()
                match = countdown_pattern.search(current_text)
                if match:
                    current_value = match.group()
                    log_time(f"Countdown: {current_value}")
                    if current_value != prev_value:
                        prev_value = current_value
                    if current_value == "00:10":
                        log_time("***** PROMPT: The countdown timer has reached 10 seconds! Switching to live active mode. *****")
                        return True
                else:
                    log_time("Countdown timer disappeared from first ss element.")
                    return False
                time.sleep(1)
            except Exception as e:
                log_time(f"Error tracking countdown: {e}")
                return False
    return False

def track_live_active_timer(driver, countdown_pattern):
    """Tracks the timer in the first live active class element."""
    try:
        live_active_elements = driver.find_elements(By.CLASS_NAME, "live")
        if not live_active_elements:
            log_time("No live active elements found.")
            return
        element = live_active_elements[0]
        log_time("Started tracking live active timer.")
        prev_value = None
        while True:
            current_text = element.text.strip()
            match = countdown_pattern.search(current_text)
            if match:
                current_value = match.group()
                log_time(f"Live active timer: {current_value}")
                if current_value != prev_value:
                    prev_value = current_value
            else:
                log_time("Live active timer disappeared.")
                break
            time.sleep(1)
    except Exception as e:
        log_time(f"Error tracking live active timer: {e}")

def main():
    try:
        log_time("Setting up WebDriver...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Uncomment to run headless
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        log_time(f"Error initializing WebDriver: {e}")
        return

    url = "https://odibets.com/odileague"
    last_class_names = []
    countdown_pattern = re.compile(r"\b\d{1,2}:\d{2}\b")

    try:
        log_time("Starting 2-minute monitoring loop...")
        while True:
            log_time("Opening OdiLeague URL...")
            driver.get(url)

            # Wait for page to load and for the ss elements to appear
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ss"))
                )
            except Exception as e:
                log_time(f"Timeout waiting for ss elements: {e}")
                time.sleep(120)
                continue

            ss_elements = driver.find_elements(By.CLASS_NAME, "ss")

            if ss_elements:
                log_time(f"Found {len(ss_elements)} ss elements.")
                # Print all ss elements' text
                for idx, element in enumerate(ss_elements, 1):
                    text = element.text.strip()
                    log_time(f"ss element {idx} text: {text}")
                save_ss_texts(ss_elements)
                last_class_names = [el.get_attribute("class").strip() for el in ss_elements]

                # Find the first ss element with a timer
                countdown_element = None
                for element in ss_elements:
                    if countdown_pattern.search(element.text):
                        countdown_element = element
                        break

                # Print all elements in the game and e class for the first ss class element
                if countdown_element:
                    game_elements = countdown_element.find_elements(By.CLASS_NAME, "game e")
                    e_elements = countdown_element.find_elements(By.CLASS_NAME, "game e")
                    for idx, game_el in enumerate(game_elements, 1):
                        log_time(f"game element {idx} text: {game_el.text.strip()}")
                    for idx, e_el in enumerate(e_elements, 1):
                        log_time(f"e element {idx} text: {e_el.text.strip()}")

                    reached_10 = track_countdown_timer(countdown_element, countdown_pattern)
                    if reached_10:
                        track_live_active_timer(driver, countdown_pattern)
                else:
                    log_time("No countdown timer found in any ss element.")
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

if __name__ == "__main__":
    main()
