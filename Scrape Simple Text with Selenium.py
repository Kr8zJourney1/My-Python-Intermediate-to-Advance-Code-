from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


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


def main():
    driver = get_driver()
    try:
        element = driver.find_element(By.XPATH, "/html/body/div[1]/div/h1[1]")
        input("Watching… press Enter to close the browser.")
        return element.text

    finally:
        driver.quit()


if __name__ == "__main__":
    print(main())
