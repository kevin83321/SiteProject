# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng
# 所有可交易標的
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.27
# Update: update modules
# Version: 1

__updated__ = '2021-02-28 23:07:13'

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup as bs
from modules import Tele, Mongo
from Config import header

def requestStockInfo(ticker, i=0):
    try:
        payload = {
            'encodeURIComponent': '1',
            'step': '1',
            'firstin': '1',
            'off': '1',
            'keyword4': '',
            'code1': '',
            'TYPEK2': '',
            'checkbtn': '',
            'queryName': 'co_id',
            'inpuType': 'co_id',
            'TYPEK': 'all',
            'co_id': ticker,
        }

        url = 'https://mops.twse.com.tw/mops/web/ajax_t05st03'

        columns = ['股票代號', '產業類別', '營利事業統一編號', '實收資本額', '已發行普通股數或TDR原股發行股數', '特別股', '電話', '地址', '主要經營業務']
        res = requests.post(url, headers=header, data=payload)
        soup = bs(res.content, 'lxml')
        table = soup.find_all('table')[1]
        cols = [th.text.strip() for th in table.find_all('th') if th.text.strip() != '本公司']
        datas = [td.text.strip() for td in table.find_all('td')]
        tmp_dict = dict((k, v) for k, v in zip(cols, datas))
        tmp_dict['已發行普通股數或TDR原股發行股數'] = float(tmp_dict['已發行普通股數或TDR原股發行股數'].split('\n')[0][:-1].replace(',', ''))
    except requests.exceptions.ConnectionError:
        i += 1
        time.sleep(10)
        if i >= 10:
            return {}
        return requestStockInfo(ticker, i)
    else:
        return tmp_dict

def GetStockTickers():
    client = Mongo()
    table = client['admin']['TWSE']['StockList']
    updateDate = list(table.distinct('UpdateDate'))[-1]
    datas = table.find({'UpdateDate':{'$eq':updateDate}, 'AssetType':{'$eq':'股票'}})
    return [x['Ticker'] for x in datas]

def ParseInfos(tickers):
    full_data = []
    for ticker in tickers:
        print(f'request {ticker}')
        temp_data = requestStockInfo(ticker)
        if temp_data:
            full_data.append(temp_data)
        time.sleep(15)
    return full_data

def updateInfo(datas):
    client = Mongo()
    table = client['admin']['Stock.Info']
    cnt = table.count_documents({})
    if not cnt:
        table.create_index([('股票代號', 1)], unique=True)
        table.insert_many(datas)
    else:
        old_df = table.find({})
        _id_mapping = dict((x['股票代號'], x['_id']) for x in old_df)
        for data in datas:
            try:
                data.update({'_id':_id_mapping[data['股票代號']]})
            except:
                pass
            if '_id' in data:
                table.update_one({'_id':data['_id']}, {'$set':data}, upsert=True)
            else:
                table.update_one(data, {'$set':data}, upsert=True)
                
def UpdateOldData():
    client = Mongo()
    table = client['admin']['Stock.Info']
    old_df = table.find({})
    for data in old_df:
        try:
            data['已發行普通股數或TDR原股發行股數'] = float(data['已發行普通股數或TDR原股發行股數'].split('\n')[0][:-1].replace(',', ''))
        except:
            pass
        if '_id' in data:
            table.update_one({'_id':data['_id']}, {'$set':data}, upsert=True)
        else:
            table.update_one(data, {'$set':data}, upsert=True)

if __name__ == '__main__':
    start = time.time()
    tickers = GetStockTickers()
    final_datas = ParseInfos(tickers)
    updateInfo(final_datas)
    # UpdateOldData()
    duration = (time.time() - start) / 60
    Tele().sendMessage(f'Update Stock Info success use {duration} mins', group='UpdateMessage')
    
    