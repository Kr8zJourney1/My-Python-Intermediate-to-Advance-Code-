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
import re


WAIT_SECS = 5
QUIET_MS = 0.6  # how long the page must stay quiet before we stop trying
OUTPUT_DIR = Path("output")
INTERVAL = 2          # seconds
COUNT = 12            # total scrapes/files


def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Selenium 4+ manages chromedriver
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    })
    driver = webdriver.Chrome(options=options)
    driver.get("https://automated.pythonanywhere.com/login/")
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


def write_timestamped_file(i: int, content: str) -> Path:
    """
    Create 'YYYY-MM-DD_HH-MM-SS lesson scrape.txt' and write `content` into it.
    Returns the created path.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = OUTPUT_DIR / f"{ts} lesson scrape.txt"
    path.write_text(content, encoding="utf-8")
    return path


def login_once(driver) -> None:
    """Log in a single time and land on the page that shows the temperature."""
    time.sleep(2)
    driver.find_element(By.ID, "id_username").send_keys("automated")
    time.sleep(2)
    driver.find_element(By.ID, "id_password").send_keys(
        "automatedautomated" + Keys.RETURN)

    time.sleep(2)
    # Click "Home" (top-left brand link) to reach the page with the temperature
    driver.find_element(By.XPATH, "/html/body/nav/div/a").click()
    time.sleep(2)


def handle_popups_in_sequence(driver, t1=8, t2=4):
    """
    1) Wait for the site's 'Change your password' popup and click its OK button.
    2) Then dismiss Chrome's 'Save password?' prompt (best-effort via ESC).
    Adjust the selectors for your site's modal.
    """
    wait = WebDriverWait(driver, t1)

    # ---------- POPUP #1: Site modal "Change your password" ----------
    try:
        # A) Find the modal/container by heading/text (example XPath):
        #    If your modal has a unique id/class, prefer CSS like:  By.CSS_SELECTOR, "#changePwModal"
        modal = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'change your password')][ancestor-or-self::*[contains(@class,'modal') or @role='dialog']][1]"
        )))

        # B) Find and click the OK/Continue button inside that modal
        #    Try common button labels; adjust if your button text differs.
        try:
            ok_btn = modal.find_element(
                By.XPATH, ".//button[normalize-space()='OK' or normalize-space()='Ok' or normalize-space()='Continue']")
        except Exception:
            # Fallback: first visible button in the modal
            ok_btn = modal.find_element(By.CSS_SELECTOR, "button, .btn")
        _safe_click(driver, ok_btn)

        # C) Wait for the modal/backdrop to go away (best-effort)
        try:
            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, ".modal.show, .modal-backdrop, [role='dialog']"))
            )
        except TimeoutException:
            pass
    except TimeoutException:
        # The change-password modal didn’t appear in time; continue anyway
        pass

    # ---------- POPUP #2: Chrome “Save password?” ----------
    # Not in DOM; send ESC to close if it appears.
    try:
        # Send ESC to the active element, then to the page as a fallback
        try:
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        except Exception:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.15)
    except Exception:
        pass


def _safe_click(driver, el):
    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)


def scrape_value(driver) -> float:
    """
    Find a visible element that actually includes a number (e.g., 24.2) and return it as float.
    Tries several sensible spots, then falls back to scanning nearby text.
    """
    wait = WebDriverWait(driver, WAIT_SECS)

    # Try likely selectors first (add/adjust if you learn the exact one)
    preferred_locators = [
        # e.g., <span id="temperature">24.2</span>
        (By.CSS_SELECTOR, "#temperature"),
        # common class/data attr
        (By.CSS_SELECTOR, ".temperature, .temp, [data-temperature]"),
        (By.XPATH, "//h1[contains(., 'Current') or contains(., 'Average')]"),
        (By.XPATH,
         "//h1[contains(., 'temperature')]/following::*[self::p or self::span or self::div][1]"),
        (By.XPATH, "(//h1)[2]"),  # your original fallback
    ]

    # 1) Try each preferred locator and parse the first numeric value
    for by, sel in preferred_locators:
        try:
            el = wait.until(EC.visibility_of_element_located((by, sel)))
            # Try the element's own text
            try:
                return clean_text(el.text)
            except ValueError:
                # Sometimes the number is in a child node
                for child in el.find_elements(By.XPATH, ".//*"):
                    try:
                        return clean_text(child.text)
                    except ValueError:
                        continue
        except TimeoutException:
            continue

    # 2) Fallback sweep: scan visible candidates on the page for any digits
    candidates = driver.find_elements(
        By.XPATH, "//*[normalize-space(string())!='']")
    for el in candidates:
        try:
            if not el.is_displayed():
                continue
            txt = el.text.strip()
            if not txt:
                continue
            try:
                return clean_text(txt)
            except ValueError:
                continue
        except StaleElementReferenceException:
            continue

    # 3) Last-resort debug artifacts so you can inspect what the page actually had
    Path("debug.html").write_text(driver.page_source, encoding="utf-8")
    driver.save_screenshot("debug.png")
    raise RuntimeError(
        "Could not find a numeric temperature on the page. See debug.html/debug.png")


def run_series(driver, count: int = COUNT, interval: int = INTERVAL):
    start = time.monotonic()
    wait = WebDriverWait(driver, WAIT_SECS)

    for i in range(1, count + 1):
        # Optional, but common for that demo site to update the value:
        # driver.refresh()

        # Ensure page has at least some headings/text present before scraping
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        except TimeoutException:
            pass

        value = scrape_value(driver)

        content = (
            f"Lesson scrape #{i}\n"
            f"Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"Value: {value}\n"
        )
        created = write_timestamped_file(i, content)
        print(f"[{i:02d}/{count}] Created -> {created.resolve()}    (Value: {value})")

        if i < count:
            next_tick = start + i * interval
            time.sleep(max(0, next_tick - time.monotonic()))


def main():
    driver = get_driver()
    try:
        login_once(driver)        # log in only once
        run_series(driver)        # then scrape/write every 2s, 12 times
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
