import os
import time

from selenium import webdriver

ROOT = os.path.abspath(os.path.dirname(__file__))
URL = "file://" + ROOT + "/qunit.html"
TIMEOUT = 5

driver = webdriver.Firefox()
driver.set_page_load_timeout(TIMEOUT)
driver.get(URL)

time.sleep(TIMEOUT)

xpath = '//div[@id="qunit-testresult-display"]/span[@class="failed"]'
element = driver.find_element_by_xpath(xpath)
count = int(element.text)
assert count == 0
driver.close()
print("ok")
