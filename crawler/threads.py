import time
from threading import Lock
from threading import Thread
from crawler.databases import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import numpy as np
import pandas as pd

from crawler.get_store_info import *

log = logging.getLogger(__name__)

done = 0
thread_lock = Lock()
info_list = []


def thread(link_list):
    global done, info_list
    log.info("Thread started")
    chrome_options = Options()
    chrome_options.binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,chrome_options=chrome_options)
    for l in link_list:
        log.info("Link: " + l)
        t = get_info(l, driver)
        t['link'] = l
        info_list.append(t)
        thread_lock.acquire()
        done += 1
        log.info("Done: " + str(done))
        thread_lock.release()
        time.sleep(1)
    driver.close()
    log.info("Thread ended")


def multi_thread_get_info(link_list, thread_number, collection, thread=thread, sleep_time=1):
    devided = np.array_split(link_list, thread_number)
    ths = []
    for d in devided:
        th = Thread(target=thread, args=[d])
        ths.append(th)
        time.sleep(sleep_time)
        th.start()
    for th in ths:
        th.join()
    try:
        add_document(info_list, collection)
    except Exception as e:
        df = pd.DataFrame(info_list)
        df.to_csv("data.csv")
        log.error("Error while adding document to collection: ")
        log.error(e)

    log.info("ALL DONE!!!!!")
    log.info(len(info_list))

    
