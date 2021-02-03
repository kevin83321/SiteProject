# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的ETF成分股
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Update: add default Adj Close as nan, run with pool
# Version: 1

__updated__ = '2021-01-30 13:12:17'

from pandas import read_csv
import os
import time
from concurrent.futures import ThreadPoolExecutor
from modules import Mongo, Tele

path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path):
    path = os.getcwd()
    
def update_data_dict(d):
    del d['Index']
    d['Adj Close'] = d['Close']
    return d

def update_one(table, d):
    table.update_one(d, {'$set':d}, upsert=True)
    time.sleep(0.001)

if __name__ == '__main__':
    client = Mongo()
    table = client['admin']['TWSE']['historicalPrice']
    table.create_index([('Date', 1), ('Ticker', 1)], unique=True)
    df = read_csv(os.path.join(path, 'TWSE_HistoricalPrice.txt'), sep='\t')
    data = [dict(x._asdict().items()) for x in df.itertuples()]

    start_time = time.time()
    with ThreadPoolExecutor(50) as executor:
        exes = [executor.submit(update_data_dict, d) for d in data]
        data = [exe.result() for exe in exes]
    table.insert_many(data)
    duration = round((time.time() - start_time) / 60, 4)
    Tele().sendMessage(f'insert {len(data)} data use {duration} mins', group='UpdateMessage')
