import sys
sys.path.append("..")

from UDPTDLTM.functions.databases import *
from UDPTDLTM.configuration import *

import os
import time
import threading
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.environ['PATH'] += unix_environ_path

logging.basicConfig(filename="logger.log",
                    filemode='w',
                    format='%(asctime)s , %(thread)d %(levelname)s : %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

db = get_database(mongodb_connection_string, "test")
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

def get_parking_lots(driver):
    checker = driver.find_element_by_xpath('''//span[@ng-bind="data.NearbyParkingPlaces.Items.length + '/' + data.NearbyParkingPlaces.Total"]''').text
    [cur, max] = checker.split('/')
    cur = int(cur)
    max = int(max)
    if max == 0:
        return []
    while cur<max:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "continueShowReview")))
        see_more_btn = driver.find_element_by_id("continueShowReview")
        see_more_btn.click()
        checker = driver.find_element_by_xpath('''//span[@ng-bind="data.NearbyParkingPlaces.Items.length + '/' + data.NearbyParkingPlaces.Total"]''').text
        cur = int(checker.split('/')[0])
    # parking_lots = driver.find_elements_by_css_selector("#res-nearby-content > div.ldc-items-list.ldc-items-row > div > ul > li")
    parking_lots = driver.find_elements_by_class_name("ldc-item-header")
    if len(parking_lots) != max:
        logging.error("Parking lot count wrong")
        return []
    pls = []
    for pl in parking_lots:
        pl_name = pl.find_element_by_class_name("ldc-item-h-name").text
        address = pl.find_elements_by_class_name("ldc-item-h-address")
        pl_position = address[0].text
        pl_opening_time = address[1].text
        pl_capacity = address[2].text
        pls.append({
            "name": pl_name,
            "address": pl_position,
            "opening_time": pl_opening_time,
            "capacity": pl_capacity
        })
    return pls

def get_info(link, driver):
    try:
        driver.get(link)
        driver.implicitly_wait(15)
        
        name = driver.find_element_by_xpath('//h1[@itemprop="name"]').text
        review_count = driver.find_element_by_class_name("microsite-review-count").text
        addr = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        district = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text

        logging.info("Getting scores")
        avg_score = driver.find_element_by_class_name("microsite-point-avg ").text
        points = driver.find_elements_by_css_selector("div.microsite-top-points > div > span")
        space_point = -1
        position_point = -1
        quality_point = -1
        serve_point = -1
        price_point = -1
        try:
            space_point = points[0].text
            position_point = points[1].text
            quality_point = points[2].text
            serve_point = points[3].text
            price_point = points[4].text
        except:
            logging.warning("Score: list index out of range")
        logging.info("Getting views and food link")
        views = driver.find_element_by_class_name("total-views").find_element_by_tag_name("span").text
        try:
            driver.find_element_by_class_name("view-all-menu").click()
            food_qr_code = driver.find_element_by_class_name("food-qrcode-footer-btn")
            food_link = food_qr_code.get_attribute("href")
            driver.find_element_by_class_name("modalCloseImg.simplemodal-close").click() # Close pop-up
        except:
            logging.info("Food link empty")
            food_link = ""
        
        t = {
            "name": name,
            "review_count": review_count,
            "address": addr,
            "district": district,
            "average_score": avg_score,
            "space_score": space_point,
            "position_score": position_point,
            "quality_score": quality_point,
            "serve_score": serve_point,
            "price_score": price_point,
            "views": views,
            "food_link": food_link,
            "food_list": [],
            "comment_list": []
        }

        logging.info("Getting other info")
        other_info = driver.find_elements_by_class_name("new-detail-info-area")
        for i in other_info:
            label = dictionary[i.find_element_by_css_selector("div:nth-child(1)").text]
            value = i.find_element_by_css_selector("div:nth-child(2)").text
            t[label] = value
            
        logging.info("Getting properties")
        micro_property = driver.find_elements_by_css_selector("div.microsite-res-info-properties > div > div > ul > li")
        t['available'] = []
        for p in micro_property:
            if p.get_attribute("class") != "none":
                t['available'].append(p.find_element_by_css_selector("a:nth-child(2)").text)
        
        logging.info("Getting branches")
        try:
            list_tools = driver.find_element_by_css_selector("ul.list-tool")
            branch_link = list_tools.find_element_by_link_text("Chi nhánh")
            # branch_link.click()
            # branch_list = driver.find_element_by_css_selector("ul.ldc-items-list.ldc-column")
            # driver.back()
            # driver.implicitly_wait(15)
        except:
            logging.info("No branch")
        logging.info("Getting parking lots")
        try:
            list_tools = driver.find_element_by_css_selector("ul.list-tool")
            parking_lot_link = list_tools.find_element_by_link_text("Bãi đỗ xe")
            parking_lot_link.click()
            t['parking_lots'] = get_parking_lots(driver)
        except:
            logging.info("No parking lot")
            t['parking_lots'] = []
        logging.info("Done link: " + link)
        return t
    except Exception as e: 
        logging.warning("Error while crawling")
        logging.error(e)

done = 0
thread_lock = threading.Lock()
def thread(link_list, collection):
    global done
    logging.info("Thread started")
    driver = webdriver.Chrome()
    for l in link_list:
        logging.info("Link: " + l)
        t = get_info(l, driver)
        try:
            add_document(t, collection)
            thread_lock.acquire()
            done += 1
            logging.info("Done: " + str(done))
            thread_lock.release()
        except Exception as e:
            logging.error("Error while adding document to collection: ")
            logging.error(e)
        time.sleep(1)
    driver.close()
    logging.info("Thread ended")

cl2 = create_collection("store_info", db)

# get_info("https://www.foody.vn/ho-chi-minh/bun-bo-hue-thanh-huong-mai-van-vinh", webdriver.Chrome())
# for i in documents["href"]:
#     get_info(i, webdriver.Chrome())
# import numpy as np
# from threading import Thread
# THREAD_NUMBER = 4
# devided = np.array_split(documents["href"],THREAD_NUMBER)

# for d in devided:
#     th = Thread(target=thread, args=[d, cl2])
#     time.sleep(1)
#     th.start()