import sys
sys.path.append(__file__[:__file__.find('UDPTDLTM/') + 9])

from crawler.threads import *
from functions.databases import *

import pandas as pd

# For notebook: sys.path.append("..")


data = pd.read_csv('UDPTDLTM/data/Restaurant_list.csv', sep='\t', encoding='utf-8')

data['Link'] = data['Link'].apply(lambda x: "https://www.foody.vn" + x)
print(data['Unnamed: 0'])

print(data["Link"])

CONNECTION_STRING = mongodb_connection_string
db = get_database(CONNECTION_STRING, "test")
cl2 = create_collection("new_store_info", db)

# multi_thread_get_info(data['Link'][:len(data['Link'])//2+1], 15, cl2)

collection_to_csv(cl2, 'UDPTDLTM/data/store_info_updated.csv')
