import sys
sys.path.append(__file__[:__file__.find('UDPTDLTM/')+9])
# For notebook: sys.path.append("..")


from configuration import * 
from functions.databases import *
from crawler.threads import *

import pandas as pd

data = pd.read_csv('UDPTDLTM/data/Restaurant_list.csv', sep='\t', encoding='utf-8')

data['Link'] = data['Link'].apply(lambda x: "https://www.foody.vn"+x)

print(data["Link"])

CONNECTION_STRING = mongodb_connection_string
db = get_database(CONNECTION_STRING, "test")
cl2 = create_collection("stores_info", db)

# multi_thread_get_info(data['Link'][:len(data['Link'])//2+1], 17, cl2)

collection_to_csv(cl2, "UDPTDLTM/data/store_info_fixed.csv")