# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng
# 所有可交易標的
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.27
# Update: update modules
# Version: 1

__updated__ = '2021-03-13 10:28:47'

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
    asset_type = ''
    full_data = []
    for tr in soup.select('table')[1].select('tr')[1:]:
        if len(tr) <= 1:
            asset_type = tr.text.strip()
            continue
        full_data.append(parseData([tr, updateDate, asset_type]))
    return full_data

def parseData(args):
    tr, updateDate, asset_type = args
    tds = [x.text.strip() for x in tr]
    return {
        'Ticker':tds[0].split('\u3000')[0].strip(),
        'Name':tds[0].split('\u3000')[1].strip(),
        'ISINCode':tds[1],
        'IssueDate':tds[2].replace('/', '-'),
        'Market':tds[3],
        'Industry':tds[4],
        'CFICode':tds[5],
        'UpdateDate':updateDate,
        'AssetType':asset_type
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