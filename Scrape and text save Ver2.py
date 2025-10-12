import re
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import time


def get_driver():

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.get("http://automated.pythonanywhere.com")
    return driver


def clean_text(text: str) -> float:
    """
    Return the first float found in the text, e.g. 'Current temperature: 24.2' -> 24.2
    Raises if no numeric value is present.
    """
    m = re.search(r'[-+]?\d+(?:\.\d+)?', text)
    if not m:
        raise ValueError(f"No numeric value found in: {text!r}")
    return float(m.group())


def write_file(text):
    """Writes input text into a text file"""
    filename = f"{datetime.now().strftime('%Y-%m-%d.%H-%M-%S')}.txt"
    with open(filename, "w") as file:
        file.write(text)


def main():
    driver = get_driver()
    try:
        while True:
            time.sleep(2)  # pacing

            # Make sure the element is there (more reliable than blind .find_element)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/h1[2]"))
            )
            element = driver.find_element(
                By.XPATH, "/html/body/div[1]/div/h1[2]")

            # Parse a float from the text (will raise if no number)
            try:
                value = clean_text(
                    element.text or element.get_attribute("textContent") or "")
            except ValueError as e:
                print("[parse error]", e)
                continue  # skip this iteration and keep trying

            # Save one line per file (your write_file creates a new timestamped file each call)
            line = f"Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S} | Value: {value}\n"
            write_file(line)
            print("Saved:", line.strip())
    except KeyboardInterrupt:
        print("Stopping loop.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
