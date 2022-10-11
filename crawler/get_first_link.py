from configuration import *
from databases import *

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('chromedriver.exe')
# driver = webdriver

def login(username, password, driver:webdriver.Chrome):
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

def scroll_to_page_end(driver:webdriver.Chrome):
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def see_more(driver:webdriver.Chrome, max_click=200):
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = last_height + 1
    driver.implicitly_wait(15)
    count = 1
    while count<=max_click:
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope > div.pn-loadmore.fd-clearbox.ng-scope > a")))
            see_more_btn = driver.find_element_by_css_selector("#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope > div.pn-loadmore.fd-clearbox.ng-scope > a")
            see_more_btn.click()
            count += 1
            driver.implicitly_wait(15)
        except Exception as e: 
            print(e)
            break
    print(count)

def get_all_category_region_district(driver:webdriver.Chrome):
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

def get_list(district_id, max_click = 200):
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get(foody_link)
    login(foody_account['username'], foody_account['password'], driver)
    categories, regions, districts = get_all_category_region_district(driver)
    print(districts[district_id].text)
    districts[district_id].click()
    # categories[0].click()
    # regions[0].click()
    # newest_button = driver.find_element_by_css_selector("#tbt > ul > li:nth-child(2) > a")
    # newest_button.click()

    # nearest_button = driver.find_element_by_css_selector("#tbt > ul > li:nth-child(2) > a")
    # nearest_button.click()
    see_more(driver, max_click)
    scroll_to_page_end(driver)
    store_list = driver.find_element_by_css_selector("#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope")
    store_list = store_list.find_elements_by_class_name("content-item.ng-scope")
    print(len(store_list))
    l = []
    count = 0
    for s in store_list:
        count += 1
        title = s.find_element_by_class_name("title.fd-text-ellip")
        # address = s.find_element_by_class_name("desc.fd-text-ellip.ng-binding")
        # comments = s.find_element_by_css_selector("div.items-count > a:nth-child(1) > span")
        # images = s.find_element_by_css_selector("div.items-count > a:nth-child(2) > span")
        l.append({
            'store_name': title.text,
            'href': title.find_element_by_tag_name("a").get_attribute('href'),
            # 'address': address.text,
            # 'comment_count': comments.text,
            # 'image_count': images.text
        })
    print("done")
    driver.quit()
    return l

db = get_database(mongodb_connection_string, "udptdltm-database")
cl = create_collection("store_links", db)
for i in range(6, 24):
    add_document(get_list(i), cl)
