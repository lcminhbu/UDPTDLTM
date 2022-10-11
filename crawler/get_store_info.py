# import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from configuration import *

# os.environ['PATH'] += unix_environ_path


log = logging.getLogger(__name__)

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

score_dict = {
    "Phục vụ": "serve_score",
    "Chất lượng": "quality_score",
    "Không gian": "space_score",
    "Vị trí": "position_score",
    "Giá cả": "price_score"
}


def get_parking_lots(driver: webdriver.Chrome):
    checker = driver.find_element("xpath",
        '''//span[@ng-bind="data.NearbyParkingPlaces.Items.length + '/' + data.NearbyParkingPlaces.Total"]''').text
    [cur, max] = checker.split('/')
    cur = int(cur)
    max = int(max)
    if max == 0:
        return []
    while cur < max:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "continueShowReview")))
        see_more_btn = driver.find_element_by_id("continueShowReview")
        see_more_btn.click()
        checker = driver.find_element("xpath",
            '''//span[@ng-bind="data.NearbyParkingPlaces.Items.length + '/' + data.NearbyParkingPlaces.Total"]''').text
        cur = int(checker.split('/')[0])
    # parking_lots = driver.find_elements_by_css_selector("#res-nearby-content > div.ldc-items-list.ldc-items-row > div > ul > li")
    parking_lots = driver.find_elements_by_class_name("ldc-item-header")
    if len(parking_lots) != max:
        log.error("Parking lot count wrong")
        return [], -1
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
    return pls, max


def get_info(link, driver: webdriver.Chrome):
    try:
        driver.get(link)
        driver.implicitly_wait(15)

        name = driver.find_element("xpath",'//h1[@itemprop="name"]').text
        review_count = driver.find_element_by_class_name("microsite-review-count").text
        addr = driver.find_element("xpath",'//span[@itemprop="streetAddress"]').text
        district = driver.find_element("xpath",'//span[@itemprop="addressLocality"]').text

        avg_score = driver.find_element_by_class_name("microsite-point-avg ").text
        points = driver.find_elements_by_css_selector("div.microsite-top-points")
        views = driver.find_element_by_class_name("total-views").find_element_by_tag_name("span").text

        t = {
            "name": name,
            "review_count": review_count,
            "address": addr,
            "district": district,
            "average_score": avg_score,
            "views": views,
        }
        for p in points:
            try:
                try:
                    score = p.find_element_by_tag_name("span").text
                except:
                    score = -1
                    log.warning("Score not found")
                finally:
                    label = p.find_element_by_class_name("label").text
                    if label not in score_dict:
                        log.error(label + "not in dictionary")
                    else:
                        t[score_dict[label]] = score
            except:
                log.warning("Score: list index out of range")
        try:
            driver.find_element_by_class_name("view-all-menu").click()
            food_qr_code = driver.find_element_by_class_name("food-qrcode-footer-btn")
            food_link = food_qr_code.get_attribute("href")
            driver.find_element_by_class_name("modalCloseImg.simplemodal-close").click()  # Close pop-up
        except:
            log.info("Food link empty")
            food_link = ""
        t['food_link'] = food_link

        other_info = driver.find_elements_by_class_name("new-detail-info-area")
        for i in other_info:
            label = dictionary[i.find_element_by_css_selector("div:nth-child(1)").text]
            value = i.find_element_by_css_selector("div:nth-child(2)").text
            t[label] = value

        micro_property = driver.find_elements_by_css_selector("div.microsite-res-info-properties > div > div > ul > li")
        t['available'] = []
        for p in micro_property:
            if p.get_attribute("class") != "none":
                t['available'].append(p.find_element_by_css_selector("a:nth-child(2)").text)

        # log.info("Getting branches")
        # try:
        #     list_tools = driver.find_element_by_css_selector("ul.list-tool")
        #     branch_link = list_tools.find_element_by_link_text("Chi nhánh")
            # branch_link.click()
            # branch_list = driver.find_element_by_css_selector("ul.ldc-items-list.ldc-column")
            # driver.back()
            # driver.implicitly_wait(15)
        # except:
        #     log.info("No branch")
        try:
            list_tools = driver.find_element_by_css_selector("ul.list-tool")
            parking_lot_link = list_tools.find_element_by_link_text("Bãi đỗ xe")
            parking_lot_link.click()
            t['parking_lots'], t['parking_lots_ammount'] = get_parking_lots(driver)
        except:
            log.info("No parking lot")
            t['parking_lots'], t['parking_lots_ammount'] = [], 0
        return t
    except Exception as e:
        log.warning("Error while crawling")
        log.error(e)
