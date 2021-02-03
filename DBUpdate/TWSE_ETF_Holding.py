# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的ETF成分股
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Update: remove connect mongo
# Version: 1

__updated__ = '2021-01-30 13:00:46'

from pandas import DataFrame
from itertools import product
from time import time
from datetime import datetime
from modules import Tele, Mongo, crawl_json_data

def requestData(args):
    etf_ticker, etf_name = args
    url = f'https://www.cmoney.tw/etf/ashx/e210.ashx?action=GetShareholdingDetails&stockId={etf_ticker}'
    js = crawl_json_data(url)
    data = js['Data']
    return list(map(parseData, product(data, [etf_ticker], [etf_name])))

def parseData(args):
    data, etf_ticker, etf_name = args
    return {
        'Ticker':data['CommKey'],
        'Name':data['CommName'],
        'Type':data['Type'],
        'Weights':data['Weights'],
        'Unit':data['Unit'],
        'ETF_Ticker':etf_ticker,
        'ETF_Name':etf_name,
        'UpdateDate':datetime.today().strftime('%Y-%m-%d')
    }

if __name__ == '__main__':
    start_time = time()
    # connect to mongo
    client = Mongo()
    listTable = client['admin']['TWSE']['ETFList']
    
    # get last update date
    uptodate = listTable.distinct('UpdateDate')[-1]
    ETFList = DataFrame(list(listTable.find({'UpdateDate':{'$eq':uptodate}}))) # Get ETFList from DB

    # link to holding table
    holdingtable = client['admin']['TWSE']['ETFHoldings']
    holdingtable.create_index([('Ticker',1), ('Type',1), ('ETF_Ticker',1), ('UpdateDate',1)], unique=True)

    # get ETF's Holdings
    output = []
    list(map(output.extend, list(map(requestData, list(zip(ETFList.Ticker, ETFList.ShortName)))))) # 將資料整理至一個List裡面
    list(map(lambda x: holdingtable.update_one(x, {'$set':x}, upsert=True), output)) # insert to mongodb
    duration = round((time() - start_time) / 60, 2)

    # send finish message
    Tele().sendMessage(f'Update ETF Holdings success\nuse {duration} mins.', group='UpdateMessage')