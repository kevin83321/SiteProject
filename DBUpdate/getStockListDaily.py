# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的ETF成分股
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Update: update modules
# Version: 1

__updated__ = '2021-02-01 21:00:39'

import pandas as pd
import requests
from itertools import product, compress
from time import time
from datetime import datetime
from bs4 import BeautifulSoup as bs
from modules import Tele, Mongo

def requestStockList(mode):
    url = f'https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}' # 上市:2, 上櫃:4
    response = requests.get(url)
    soup = bs(response.text, 'lxml')
    updateDate = soup.select('table')[0].select('h2')[1].text.split(':')[1].strip().replace('/', '-')
    trs = list(compress(soup.select('table')[1].select('tr'), list(map(lambda x: len(x) > 1, soup.select('table')[1].select('tr')))))[1:]
    return list(map(parseData, product(trs, [updateDate])))

def parseData(args):
    tr, updateDate = args
    tds = [x.text.strip() for x in tr]
    return {
        'Ticker':tds[0].split('\u3000')[0],
        'Name':tds[0].split('\u3000')[1],
        'ISINCode':tds[1],
        'IssueDate':tds[2].replace('/', '-'),
        'Market':tds[3],
        'Industry':tds[4],
        'CFICode':tds[5],
        'UpdateDate':updateDate
    }
    
def updateOutput(args):
        """update output"""
        res, df = args
        try:
            res.update({'_id':df[df.Ticker==res['Ticker']]['_id'].values[0]})
        except:
            pass
        return res

if __name__ == '__main__':
    start_time = time()
    # connect to Mongo
    client = Mongo()
    table = client['admin']['TWSE']['StockList']
    
    # Create index
    table.create_index([('Ticker', 1), ('Name',1)], unique=True)

    # Get Exists Stocks
    ExistsStocks = pd.DataFrame(list(table.find()))

    # request stock list, Mode {2:上市, 4:上櫃}
    output = requestStockList(2) + requestStockList(4)
    
    output = list(map(updateOutput, list(product(output, [ExistsStocks]))))
    
    # insert Data
    list(map(lambda x: table.update_one({'_id':x['_id']}, {'$set':x}, upsert=True) if '_id' in x else table.update_one(x, {'$set':x}, upsert=True), output))
    
    duration = round((time() - start_time) / 60, 2)
    # print(f'Get stock list use {duration} mins')

    # send finish message
    Tele().sendMessage(f'Update Stock List success use {duration} mins', group='UpdateMessage')