# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng
# 所有可交易標的
# Author: Kevin Cheng 鄭圳宏
# Create: 2022.09.09
# Update: update modules
# Version: 1

__updated__ = '2022-09-16 15:51:43'

import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup as bs
from modules import Tele, Mongo
# from Config import header
from Log.TransforException import TransforException

def update2DB(table, datas):
    try:
        table.insert_many(datas)
    except:
        for d in datas:
            table.update_one(d, {'$set':d}, upsert=True)

def GetStockTickers():
    client = Mongo()
    table = client['admin']['TWSE']['StockList']
    updateDate = list(table.distinct('UpdateDate'))[-1]
    datas = table.find({'UpdateDate':{'$eq':updateDate}, 'AssetType':{"$in":["股票", "台灣存託憑證(TDR)",
                                                                            "台灣存託憑證", "普通股"]}})
    return [x['Ticker'] for x in datas]

def getCMKey(ticker='2330'):
    url = f'https://www.cmoney.tw/finance/ticker/f00026'
    res = requests.get(url)
    soup = bs(res.content, 'lxml')
    keys_info = soup.find_all('a', {'class':"mobi-finance-subnavi-link"})
    key_26 = ""
    # key_36 = ""
    for k in keys_info:
        # if k.get('page') == "":
        #     key_26 = k.get('cmkey')
        if k.get("page") == 'f00026':
            key_26 = k.get('cmkey')
        # if k.get("page") == 'f00036':
        #     key_36 = k.get('cmkey')
        # print(k.page)
        # print(k.get("page"), type(k))
    return key_26

def getStockInfo(ticker = "2330", cmkey=None):
    if not cmkey:
        cmkey = getCMKey(ticker)
    url = f'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetStockBasicInfo&stockId={ticker}&cmkey={cmkey}' # 
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": f"https://www.cmoney.tw/finance/{ticker}/f00026",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    pay_load = {
        "action": "GetInstitutionalInvestorsShareholding",
        "stockId": ticker,
        "cmkey": cmkey
    }
    return requests.get(url, headers=headers, data=pay_load)

def main(date = datetime.today()):
    try:
        start_time = time.time()
        client = Mongo()
        schema = client['admin']
        table_name = 'Stock.Info.Full'
        collections = schema.list_collection_names()
        db_not_found = table_name not in collections
        table = schema[table_name]
        if all([db_not_found]):
            table.create_index([('UpdateDate', 1), ('Ticker', 1)], unique=True)
        else:
            cnt = table.count()
            if not all([cnt]):
                table.create_index([('UpdateDate', 1), ('Ticker', 1)], unique=True)
        
        Tickers = GetStockTickers()
        cmkey = None
        output = []
        for ticker in Tickers:
            if not cmkey:
                cmkey = getCMKey(ticker)
            tmp_info = getStockInfo(ticker, cmkey)
            tmp_info = tmp_info.json()[0]
            # print(tmp_info)
            output.append({
                "UpdateDate":date.strftime("%Y-%m-%d"),
                "Ticker":ticker,
                "PaidInCapital":float(tmp_info['PaidInCapital']) * 1e6,
                "MarketValue":float(tmp_info['MarketPrice']) * 1e8,
                "TotalShares":float(tmp_info["PaidInCapital"]) * 1e6 / 10
            })
            time.sleep(1)
        update2DB(table, output)
        # table.insert_many(output)
        duration = time.time() - start_time
    except Exception as e:
        Tele().sendMessage('Update Stock Basic Info Failed', group='UpdateMessage')
        print(e)
    else:
        Tele().sendMessage(f'Update Stock Basic Info Success, cost {round(duration, 2)} seconds.', group='UpdateMessage')
    
if __name__ == '__main__':
    main()