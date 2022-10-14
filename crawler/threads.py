import time
from threading import Lock
from threading import Thread
from databases import *

import numpy as np
import pandas as pd
import os

from get_store_info import *

# os.environ['PATH'] += unix_environ_path
log = logging.getLogger(__name__)

done = 0
thread_lock = Lock()
info_list = []


def thread(link_list):
    global done, info_list
    log.info("Thread started")
    # driver = webdriver.Chrome()
    driver = webdriver.Edge("msedgedriver.exe")
    for l in link_list:
        try:
            log.info("Link: " + l)
            t = get_info(l, driver)
            t['link'] = l
            info_list.append(t)
            thread_lock.acquire()
            done += 1
            log.info("Done: " + str(done))
            thread_lock.release()
            time.sleep(1)
        except Exception as e:
            log.error("Error while crawling")
            log.error(e)
            print(l)
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
    
