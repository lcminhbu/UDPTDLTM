import pandas as pd
import os

import sys
sys.path.append(__file__[:__file__.find('UDPTDLTM/') + 9])

dirs = os.listdir('UDPTDLTM/data/Menu')
df = pd.read_csv('UDPTDLTM/data/Menu/'+dirs[0], sep='\t', encoding='utf-8')

for f in dirs[1:]:
    frames = [df, pd.read_csv('UDPTDLTM/data/Menu/'+f, sep='\t', encoding='utf-8')]
    df = pd.concat(frames, ignore_index=True)

df = df.drop(columns='Unnamed: 0')
df.to_csv('UDPTDLTM/data/menu.csv')
