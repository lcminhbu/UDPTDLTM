from get_store_info import *
import pandas as pd
import numpy as np
from threading import Thread
data = pd.read_csv('data/Restaurant_list.csv', sep='\t', encoding='utf-8')

data['Link'] = data['Link'].apply(lambda x: "https://www.foody.vn"+x)

print(data["Link"])

CONNECTION_STRING = "mongodb+srv://username:Password123@cluster0.g3tu9j6.mongodb.net/test"
db = get_database(CONNECTION_STRING, "test")
cl2 = create_collection("store_info", db)

THREAD_NUMBER = 10
devided = np.array_split(data['Link'],THREAD_NUMBER)

for d in devided:
    th = Thread(target=thread, args=[d, cl2])
    time.sleep(1)
    th.start()