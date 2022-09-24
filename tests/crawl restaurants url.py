from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.by import By
import copy
import time
import os

os.environ['PATH'] += '/usr/lib/chromium/chromium'

driver = webdriver.Chrome()
wait_time = 3

restaurants_df = pd.DataFrame(columns=['City','Restaurant','URL'])
restaurants_df

def scrollToPageEnd(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def createRestaurantsDF(url, city):

    driver.get(url)

    time.sleep(wait_time)

    dummy0 = driver.find_element_by_xpath('//div[@class="nav-box"]')

    time.sleep(wait_time)

    scrollToPageEnd(driver)

    time.sleep(wait_time)

    dummy2 = driver.find_element_by_xpath('//*[@id="ajaxRequestDiv"]/div/div[2]')

    dummy3 = driver.find_elements_by_xpath('.//div[@class="content-item ng-scope"]')
    
    temp_df = pd.DataFrame(columns=['City','Restaurant','URL'])
    
    for elem in dummy3:
        record = {
            "City": city,
            "Restaurant": elem.find_element_by_xpath('.//div[@class="title fd-text-ellip"]').text,
            "URL": elem.find_element_by_xpath('.//div[@class="title fd-text-ellip"]/a').get_attribute('href')
        }
        temp_df = temp_df.append(record, ignore_index=True)
     
    return temp_df 

temp_df = createRestaurantsDF("https://www.foody.vn/ho-chi-minh", "TP.HCM")
    
restaurants_df = pd.concat([restaurants_df,temp_df], ignore_index=True)

restaurants_df

restaurants_df.to_csv("Restaurants_URL.csv", index=False, header=True, columns=restaurants_df.columns)