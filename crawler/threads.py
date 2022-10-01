import time
from threading import Lock
from threading import Thread
from functions.databases import *

import numpy as np

from crawler.get_store_info import *

log = logging.getLogger(__name__)

done = 0
thread_lock = Lock()


def thread(link_list, collection):
    global done
    log.info("Thread started")
    driver = webdriver.Chrome()
    for l in link_list:
        log.info("Link: " + l)
        t = get_info(l, driver)
        t['link'] = l
        try:
            add_document(t, collection)
            thread_lock.acquire()
            done += 1
            log.info("Done: " + str(done))
            thread_lock.release()
        except Exception as e:
            log.error("Error while adding document to collection: ")
            log.error(e)
        time.sleep(1)
    driver.close()
    log.info("Thread ended")


def multi_thread_get_info(link_list, thread_number, collection, thread=thread, sleep_time=1):
    devided = np.array_split(link_list, thread_number)

    for d in devided:
        th = Thread(target=thread, args=[d, collection])
        time.sleep(sleep_time)
        th.start()
