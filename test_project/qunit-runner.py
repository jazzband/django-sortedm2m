import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

ROOT = os.path.abspath(os.path.dirname(__file__))
URL = "file://" + ROOT + "/qunit.html"
TIMEOUT = 5

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(TIMEOUT)
driver.get(URL)

time.sleep(TIMEOUT)

xpath = '//div[@id="qunit-testresult-display"]/span[@class="failed"]'
element = driver.find_element(by=By.XPATH, value=xpath)
count = int(element.text)
assert count == 0
driver.close()
print("ok")
