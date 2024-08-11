import os
import time

from selenium import webdriver  # pylint:disable=no-name-in-module
from selenium.webdriver.common.by import By

ROOT = os.path.abspath(os.path.dirname(__file__))
URL = "file://" + ROOT + "/qunit.html"
TIMEOUT = 5

driver = webdriver.Firefox()
driver.set_page_load_timeout(TIMEOUT)
driver.get(URL)

time.sleep(TIMEOUT)

xpath = '//div[@id="qunit-testresult-display"]/span[@class="failed"]'
element = driver.find_element(by=By.XPATH, value=xpath)
count = int(element.text)
assert count == 0
driver.close()
print("ok")
