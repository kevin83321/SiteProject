# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的ETF清單
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Version: 1

__updated__ = '2021-01-30 13:01:37'

import requests, os
from bs4 import BeautifulSoup as bs
from datetime import datetime
from modules import Tele, Mongo
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): 
    path = os.getcwd()

def parseData(tr):
    tds = [td.text for td in tr.select('td')]
    return {
        'IssueDate':tds[0].replace('/', '-'),
        'Ticker':tds[1],
        'ShortName':tds[2],
        'Issuer':tds[3],
        'Underlying':tds[4],
        'UpdateDate':datetime.today().strftime('%Y-%m-%d')
    }

#%% 
if __name__ == '__main__':
    # request ETF List
    url = 'https://www.twse.com.tw/zh/page/ETF/list.html'
    response = requests.get(url)
    soup = bs(response.text, 'lxml')
    data = list(map(parseData, soup.select('table')[0].select('tr')[1:]))

    # connect to Mongo
    client = Mongo()
    table = client['admin']['TWSE']['ETFList']
    
    # Create index
    table.create_index([('Ticker',1), ('UpdateDate',1)], unique=True)

    #insert Data
    list(map(lambda x: table.update_one(x, {'$set':x}, upsert=True), data))

    # send finish message
    # Line().sendMessage('Update ETF List success')
    Tele().sendMessage('Update ETF List success', group='UpdateMessage')