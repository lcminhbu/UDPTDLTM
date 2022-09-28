from bs4 import BeautifulSoup
import requests
import requests_cache
# YOUR CODE HERE (OPTION)
# Nếu cần các thư viện khác thì bạn có thể import ở đây
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from threading import Thread
import random
import urllib
import pandas as pd
import logging


# Thread that return value
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def get_restaurant_link(pages_list):
    restaurant_list = []
    for page in pages_list:
        url = f"https://www.foody.vn/ho-chi-minh/dia-diem?ds=Restaurant&vt=row&st=1&page={page}&provinceId=217&categoryId=&append" \
              "=true "
        driver = webdriver.Edge()
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        data = soup.findAll("h2")
        for index in data:
            href = index.contents
            if "Hệ thống" in index.text:
                restaurant_list.extend(handle_restaurant_chain_link(href[6]['href']))
            else:
                restaurant_list.append([href[3]['href'], href[3].text])
    return restaurant_list


def handle_restaurant_chain_link(link):
    restaurant_list = []
    driver = webdriver.Edge()
    driver.get("https://www.foody.vn/" + link)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    data = soup.findAll("h2")
    for index in data:
        href = index.contents
        restaurant_list.append([href[1]['href'], href[1].text])

    return restaurant_list


def handle_restaurant_page(link_list):
    metadata_list = []
    for index in range(len(link_list)):
        print(f"{index}-{len(link_list)}")
        try:
            driver = webdriver.Edge()
            driver.get("https://www.foody.vn/" + link_list[index])
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.close()
            metadata = [link_list[index]]
            name = soup.find('h1', itemprop="name").text
            metadata.append(name)
            total_rate = soup.find(itemprop="ratingValue")
            if total_rate is not None:
                metadata.append(total_rate.text.replace('\n', '').strip())
            else:
                metadata.append(None)
            points = soup.findAll("div", class_="microsite-top-points")
            points_list = {}
            for point in points:
                rate = point.contents[1].text.replace('\n', '')
                points_list[point.contents[3].text] = rate
            # "space_score", "position_score", "quality_score", "serve_score", "price_score"
            metadata.append(points_list['Không gian'])
            metadata.append(points_list['Vị trí'])
            metadata.append(points_list['Chất lượng'])
            metadata.append(points_list['Phục vụ'])
            metadata.append(points_list['Giá cả'])
            address = soup.find('span', itemprop="streetAddress")
            district = soup.find('span', itemprop="addressLocality")
            views = soup.findAll(class_='total-views')
            review_count = soup.findAll(class_="microsite-review-count")
            open_hours = soup.find(class_="micro-timesopen")
            if open_hours is not None:
                open_hours = open_hours.contents[5].text.replace('\xa0', '').split('-')
            else:
                open_hours = [None, None]
            price_range = soup.find('span', itemprop="priceRange")
            if price_range is not None:
                price_range = price_range.text.replace('\n', '')
            else:
                price_range = None
            infor_area = soup.findAll(class_='new-detail-info-area')
            metadata.append(address.text)
            metadata.append(district.text)
            metadata.append(views[0].text.replace("lượt xem", '').replace('\n', ''))
            metadata.append(review_count[0].text)
            metadata.append(price_range)
            metadata.extend([open_hours[0], open_hours[-1]])
            need_to_remove = ["Thích hợp", "Giờ nhận khách cuối", "Thời gian chuẩn bị", "Nghỉ lễ", "Thể loại", "Sức chứa",
                              "Phong cách ẩm thực", "Phù hợp với", "Phục vụ các món"]
            infor_check = {}
            for index in need_to_remove:
                infor_check[index] = None
            for index in infor_area:
                for title in need_to_remove:
                    if title in index.text:
                        infor_check[title] = index.text.replace(title, "").replace('\n', "").replace('\xa0','').strip()
                        break
            for index in need_to_remove:
                metadata.append(infor_check[index])
            available = soup.findAll(class_="microsite-box-content")[-1]
            available = [index for index in available.text.split('\n') if index !=""]
            metadata.append(available)
            metadata_list.append(metadata)
        except:
            print("An exception occurred")
    return metadata_list


def get_all_page_link_main():
    pages = list(range(1, 169))
    n = 15
    data_divide = [pages[i:i + n] for i in range(0, len(pages), n)]
    print(len(data_divide))
    my_threads = []
    final = []
    print("------------------------------------------")
    for index in range(len(data_divide)):
        thread = ThreadWithReturnValue(target=get_restaurant_link, args=([data_divide[index]]))
        thread.start()
        print(index)
        my_threads.append(thread)
    for index in my_threads:
        final.extend(index.join())
    dataframe = pd.DataFrame(final, columns=['Link', 'Name'])
    dataframe.to_csv('Restaurant_list.csv', sep='\t', encoding='utf-8')


def get_page_information(csv_file):
    page_information = []
    data = pd.read_csv(csv_file, sep='\t', encoding='utf-8')
    links = data['Link'].tolist()[-2182:]  # -2182
    n = 200
    data_divide = [links[i:i + n] for i in range(0, len(links), n)]
    print(len(data_divide))
    my_threads = []
    for index in range(len(data_divide)):
        thread = ThreadWithReturnValue(target=handle_restaurant_page, args=([data_divide[index]]))
        thread.start()
        print(index)
        my_threads.append(thread)
    for index in my_threads:
        page_information.extend(index.join())
    dataframe = pd.DataFrame(page_information,
                             columns=["Link", "Name", "average_score", "space_score", "position_score", "quality_score",
                                      "serve_score", "price_score", "address", "district", "views", "review_count",
                                      "price_range", "open hours", "close hours", "suitable_time", "last_pickup_time",
                                      "prepare_time", "holiday", "type", "capacity", "style", "suitable_with",
                                      "serves","available"])
    dataframe.to_csv('Restaurant_information.csv', sep='\t', encoding='utf-8')


# if __name__ == "__main__":
#test = handle_restaurant_page(['ho-chi-minh/morico-modern-japanese-restaurant-cafe-le-loi','ho-chi-minh/tuktuk-thai-bistro-hoa-mai'])
data = pd.read_csv('Restaurant_information.csv', sep='\t', encoding='utf-8')
#get_page_information('Restaurant_list.csv')
print(1)
