import sys
sys.path.append(__file__[:__file__.find('UDPTDLTM/')+9])
# For notebook: sys.path.append("..")


from configuration import * 
from functions.databases import *
from crawler.threads import *

import pandas as pd

data = pd.read_csv('data/Restaurant_list.csv', sep='\t', encoding='utf-8')

data['Link'] = data['Link'].apply(lambda x: "https://www.foody.vn"+x)

print(data["Link"])

CONNECTION_STRING = mongodb_connection_string
db = get_database(CONNECTION_STRING, "test")
cl2 = create_collection("stores_info", db)

# THREAD_NUMBER = 15
# devided = np.array_split(data['Link'][:len(data['Link'])//2+1],THREAD_NUMBER)

# for d in devided:
#     th = Thread(target=thread, args=[d, cl2])
#     time.sleep(1)
#     th.start()


multi_thread_get_info(data['Link'], 4, cl2)