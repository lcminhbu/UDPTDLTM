from functions.databases import *
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from threading import Thread
import numpy as np


os.environ['PATH'] += '/usr/lib/chromium/chromium'



CONNECTION_STRING = "mongodb+srv://username:Password123@cluster0.g3tu9j6.mongodb.net/test"

db = get_database(CONNECTION_STRING, "test")
cl = create_collection("store_link", db)

documents = get_all_documents(cl)

dictionary = {
    "Thời gian hoạt động": "opening_time",
    "Thích hợp": "suitable_time",
    "Thời gian chuẩn bị": "prepare_time",
    "Nghỉ lễ": "holiday",
    "Thể loại": "type",
    "Sức chứa": "capacity",
    "Phong cách ẩm thực": "style",
    "Phù hợp với": "suitable_with",
    "Phục vụ các món": "serves",
    "Khoảng giá khác": "price_range",
    "Giờ nhận khách cuối": "last_pick_up_time",
    "Website": "website"
}

def see_more(driver):
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = last_height + 1
    driver.implicitly_wait(15)
    while True:
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            see_more_btn = driver.find_element_by_id("continueShowReview")
            WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.ID, "continueShowReview")))
            see_more_btn.click()
            driver.implicitly_wait(10)
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
    
def get_info(link):
    try:
        driver = webdriver.Chrome()
        driver.get(link)
        driver.implicitly_wait(15)
        avg_score = driver.find_element_by_class_name("microsite-point-avg ").text

        points = driver.find_elements_by_class_name("microsite-top-points")
        try:
            space_point = points[0].find_element_by_class_name("avg-txt-highlight").text
        except:
            print("RED")
            space_point = points[0].text
        try:
            position_point = points[1].find_element_by_class_name("avg-txt-highlight").text
        except:
            position_point = points[1].text
        try:
            quality_point = points[2].find_element_by_class_name("avg-txt-highlight").text
        except:
            quality_point = points[2].text
        try:
            serve_point = points[3].find_element_by_class_name("avg-txt-highlight").text
        except:
            serve_point = points[3].text
        try:
            price_point = points[4].find_element_by_class_name("avg-txt-highlight").text
        except:
            price_point = points[4].text
    
        views = driver.find_element_by_class_name("total-views").find_element_by_tag_name("span").text
        try:
            driver.find_element_by_class_name("view-all-menu").click()
            food_qr_code = driver.find_element_by_class_name("food-qrcode-footer-btn")
            food_link = food_qr_code.get_attribute("href")
            close_btn = driver.find_element_by_class_name("modalCloseImg.simplemodal-close")
            close_btn.click()
        except:
            print("EMPTY")
            food_link = ""
            
        other_info = driver.find_elements_by_class_name("new-detail-info-area")
        t1 = {}
        for i in other_info:
            label = dictionary[i.find_element_by_css_selector("div:nth-child(1)").text]
            value = i.find_element_by_css_selector("div:nth-child(2)").text
            t1[label] = value
            
        micro_property = driver.find_elements_by_css_selector("div.microsite-res-info-properties > div > div > ul > li")
        available = []
        for p in micro_property:
            if p.get_attribute("class") != "none":
                available.append(p.find_element_by_css_selector("a:nth-child(2)").text)
        
        try:
            list_tools = driver.find_element_by_css_selector("ul.list-tool")
            branch_link = list_tools.find_element_by_link_text("Chi nhánh")
            branch_link.click()
            branch_list = driver.find_element_by_css_selector("ul.ldc-items-list.ldc-column")
            driver.back()
            driver.implicitly_wait(15)
            print("Có chi nhánh")
        except:
            print("Ko có chi nhánh")
        try:
            list_tools = driver.find_element_by_css_selector("ul.list-tool")
            parking_lot_link = list_tools.find_element_by_link_text("Bãi đỗ xe")
            parking_lot_link.click()
            see_more(driver)
            parking_lots = driver.find_elements_by_css_selector("#res-nearby-content > div.ldc-items-list.ldc-items-row > div > ul > li")
            pls = []
            for pl in parking_lots:
                pl_name = pl.find_element_by_class_name("ldc-item-h-name").text
                address = pl.find_elements_by_class_name("ldc-item-h-address")
                try:
                    pl_position = address[0].text
                    pl_opening_time = address[1].text
                    pl_capacity = address[2].text
                    pls.append({
                        "name": pl_name,
                        "address": pl_position,
                        "opening_time": pl_opening_time,
                        "capacity": pl_capacity
                    })
                except:
                    print("ERRORRRR")
                    print(len(address))
            print("Có bãi xe")
        except:
            print("Không có bãi xe")
            pls = []
        driver.close()
        t2 = {
            "average_score": avg_score,
            "space_score": space_point,
            "position_score": position_point,
            "quality_score": quality_point,
            "serve_score": serve_point,
            "price_score": price_point,
            "views": views,
            "food_link": food_link,
            "other_info": available,
            "parking_lots": pls,
            "food_list": [],
            "comment_list": []
        }
        t2.update(t1)
        return t2
    except Exception as e: 
        print(e)
        print(link)
            
def thread(link_list, collection): 
    for l in link_list:
        add_document(get_info(l), collection)
        time.sleep(2)


cl2 = create_collection("store_info", db)
# for i in documents["href"]:
#     get_info(i)
THREAD_NUMBER = 4
devided = np.array_split(documents["href"],THREAD_NUMBER)

for d in devided:
    th = Thread(target=thread, args=[d, cl2])
    time.sleep(2)
    th.start()
