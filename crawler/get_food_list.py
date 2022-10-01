from configuration import *
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

log = logging.getLogger(__name__)

driver = webdriver.Chrome()

driver.get('https://shopeefood.vn/ho-chi-minh/bun-dau-homemade-phan-xich-long?source_url=foody_ordernow_pc')
driver.implicitly_wait(15)

divs = driver.find_elements_by_css_selector('.ReactVirtualized__Grid__innerScrollContainer > div')


# d = driver.execute_script(driver.find_elements_by_css_selector('.ReactVirtualized__Grid__innerScrollContainer > div'))
def scroll_to_page_end(driver: webdriver.Chrome, pixel, s):
    search = driver.find_element_by_class_name('search-items')
    b = search.location['y'] + search.size['height']
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(f"window.scrollTo(0, {pixel + s.size['height']});")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


print(len(divs))
for div in divs:
    print(div.text)
    print(div.location['y'])
scroll_to_page_end(driver, divs[-1].location['y'], divs[-1])
