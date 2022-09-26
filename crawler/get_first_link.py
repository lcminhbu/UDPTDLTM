import sys
sys.path.append("..")

from UDPTDLTM.configuration import *
from UDPTDLTM.functions.databases import *

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


os.environ['PATH'] += unix_environ_path

driver = webdriver.Chrome()

driver.get(foody_link)

def login(username, password):
    login_button = driver.find_element_by_css_selector("#accountmanager > a")
    login_button.click()
    driver.implicitly_wait(15)
    username_field = driver.find_element_by_id("Email")
    username_field.send_keys(username)
    password_field = driver.find_element_by_id("Password")
    password_field.send_keys(password)
    login = driver.find_element_by_id("bt_submit")
    login.click()
    driver.implicitly_wait(15)

def scroll_to_page_end(driver):
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def see_more():
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = last_height + 1
    driver.implicitly_wait(15)
    count = 1
    while count<=2:
        print(count)
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            WebDriverWait(driver, 30).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope > div.pn-loadmore.fd-clearbox.ng-scope > a")))
            see_more_btn = driver.find_element_by_css_selector("#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope > div.pn-loadmore.fd-clearbox.ng-scope > a")
            see_more_btn.click()
            count += 1
            driver.implicitly_wait(15)
            while True:
                last_height = new_height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height > last_height:
                    break
                else:
                    time.sleep(SCROLL_PAUSE_TIME)
        except Exception as e: 
            print(e)
            break

def get_all_category_region_district():
    category_element = driver.find_element_by_css_selector("#tbt > ul > li:nth-child(7) > select")
    categories = category_element.find_elements_by_tag_name("option")
    categories.remove(categories[0])
    region_element = driver.find_element_by_css_selector("#tbt > ul > li:nth-child(6) > select")
    regions = region_element.find_elements_by_tag_name("option")
    regions.remove(regions[0])
    district_element = driver.find_element_by_id("slDistrictPlace")
    districts = district_element.find_elements_by_tag_name("option")
    districts.remove(districts[0])

    return categories, regions, districts

login(foody_account['username'], foody_account['password'])

categories, regions, districts = get_all_category_region_district()

# categories[0].click()
# regions[0].click()
# newest_button = driver.find_element_by_css_selector("#tbt > ul > li:nth-child(2) > a")
# newest_button.click()

# nearest_button = driver.find_element_by_css_selector("#tbt > ul > li:nth-child(2) > a")
# nearest_button.click()
districts[0].click()

see_more()
scroll_to_page_end(driver)

store_list = driver.find_element_by_css_selector("#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope")
store_list = store_list.find_elements_by_class_name("content-item.ng-scope")
print(len(store_list))


db = get_database(mongodb_connection_string, "test")
cl = create_collection("store_link", db)
for s in store_list:
    title = s.find_element_by_class_name("title.fd-text-ellip")
    address = s.find_element_by_class_name("desc.fd-text-ellip.ng-binding")
    comments = s.find_element_by_css_selector("div.items-count > a:nth-child(1) > span")
    images = s.find_element_by_css_selector("div.items-count > a:nth-child(2) > span")
    document = {
        'store_name': title.text,
        'href': title.find_element_by_tag_name("a").get_attribute('href'),
        'address': address.text,
        'comment_count': comments.text,
        'image_count': images.text
    }
    add_document(document, cl)

print(get_all_documents(cl))