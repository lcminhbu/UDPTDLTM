import time
from random import randint
from threading import Thread
from pymongo import MongoClient
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from configuration import *


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


def handle_menu(link_list, mongodb_collection):
    menu_list = []
    for index in range(len(link_list)):
        print(f"{index}-{len(link_list)}")
        menu = []
        try:
            driver = webdriver.Edge()
            print(link_list[index])
            driver.get("https://www.shopeefood.vn" + link_list[index])
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            check_available = soup.find(class_="txt-bold font15")
            if check_available and check_available.text == "Rất tiếc, bài viết không tồn tại !":
                driver.close()
                menu_list.append(
                    [link_list[index], None, None])
                mongodb_collection.insert_one(
                    {'Link': 'https://www.foody.vn' + link_list[index], 'Food_Name': None,
                     'Price': None})
            else:
                body = driver.find_element(by=By.CSS_SELECTOR, value="body")
                for dump in range(50):
                    if dump != 0:
                        body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(0.5)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    data_sample = soup.findAll(class_="item-restaurant-row")
                    menu.extend(data_sample)
                driver.close()
                menu = pd.unique(menu).tolist()
                for disk in menu:
                    menu_list.append(
                        [link_list[index], disk.find_next(text=True).strip(), disk.contents[0].contents[2].text])
                    mongodb_collection.insert_one(
                        {'Link': 'https://www.foody.vn'+link_list[index], 'Food_Name': disk.find_next(text=True).strip(),
                         'Price': disk.contents[0].contents[2].text})
                time.sleep(randint(1, 4))
        except Exception as e:
            print(e)

    return menu_list


def get_menu_information(link_dataframe, start_index, end_index, mongodb_collection, thread=10):
    menu = []
    links = link_dataframe['href'].tolist()[start_index:end_index]
    print(len(links))
    links = [index.replace('https://www.foody.vn', '') for index in links]
    divide = int(len(links)/thread)
    data_divide = [links[i:i + thread] for i in range(0, len(links), divide)]
    print(len(data_divide))
    my_threads = []
    for index in range(len(data_divide)):
        thread = ThreadWithReturnValue(target=handle_menu, args=([data_divide[index], mongodb_collection]))
        thread.start()
        print(index)
        my_threads.append(thread)
    for index in my_threads:
        menu.extend(index.join())
    dataframe = pd.DataFrame(menu,
                             columns=["Link", "Food_name", "Price"])
    dataframe.to_csv('Menu.csv', sep='\t', encoding='utf-8')


if __name__ == "__main__":
    db_link = MongoClient(mongodb_connection_string_link)
    link_collection = db_link["udptdltm-database"]["store_links"]
    link_dataframe = pd.DataFrame(link_collection.find())
    db_menu = MongoClient(mongodb_connection_string_menu)
    # LƯU Ý
    # test-menu dùng để test
    # official-menu dùng cho chính thức
    menu_collection = db_menu['menu']['test-menu']
    # muốn bao nhiêu thread thì set tham số thread = ...
    # 16GB RAM thì tầm 10-12 thread là lag rồi, nên cân nhắc
    # Đăng: 0->5804
    # Thái: 5805->11609
    # Duy: 11610->17414
    # Thắng: 17415->23219
    # Bửu: 23220->29024
    # ví dụ lấy từ index 0->29
    get_menu_information(link_dataframe, 0, 30, menu_collection)
