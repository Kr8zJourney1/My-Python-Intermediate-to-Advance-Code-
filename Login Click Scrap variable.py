from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys


def get_driver():

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.get("http://automated.pythonanywhere.com/login/")
    return driver


def clean_text(text):
    """Extract only the temperature from text"""
    output = float(text.split(": ")[1])
    return output


def login():
    driver = get_driver()
    time.sleep(2)
    driver.find_element(by="id", value="id_username").send_keys("automated")
    time.sleep(2)
    driver.find_element(by="id", value="id_password").send_keys(
        "automatedautomated" + Keys.RETURN)

    time.sleep(2)
    print(driver.current_url)
    driver.find_element(by="xpath", value="/html/body/nav/div/a").click()
    time.sleep(2)
    element = driver.find_element(
        by="xpath", value="/html/body/div[1]/div/h1[2]")
    return clean_text(element.text)


print(login())
