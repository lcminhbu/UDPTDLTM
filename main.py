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
    driver.get("https://www.foody.vn/"+link)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    data = soup.findAll("h2")
    for index in data:
        href = index.contents
        restaurant_list.append([href[1]['href'], href[1].text])

    return restaurant_list

def handle_restaurant_page(link):
    
# if __name__ == "__main__":
#     pages = list(range(1,169))
#     n = 15
#     data_divide = [pages[i:i + n] for i in range(0, len(pages), n)]
#     print(len(data_divide))
#     my_threads = []
#     final = []
#     print("------------------------------------------")
#     for index in range(len(data_divide)):
#         thread = ThreadWithReturnValue(target=get_restaurant_link, args=([data_divide[index]]))
#         thread.start()
#         print(index)
#         my_threads.append(thread)
#     for index in my_threads:
#         final.extend(index.join())
#     dataframe = pd.DataFrame(final, columns=['Link', 'Name'])
#     dataframe.to_csv('Restaurant_list.csv', sep='\t', encoding='utf-8')

data = pd.read_csv('Restaurant_list.csv', sep='\t', encoding='utf-8')
print(1)