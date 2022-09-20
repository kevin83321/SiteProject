# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
# 爬取所有上市上櫃的股票交易日資料
# Author: Kevin Cheng 鄭圳宏
# Create: 2022.09.16
# Update: add log write into cmd
# Version: 1

__updated__ = '2022-09-17 22:52:59'
_FileTitle = "更新股票標借資料"

import requests
import time
from datetime import datetime, timedelta
from pandas import date_range, to_datetime
# from bs4 import BeautifulSoup as bs
from modules import Tele, Mongo, crawl_json_data
# from Config import header
from Log.TransforException import TransforException

cols = 'Date,Ticker,Name,Fin_Company,BidQty,BidPriceH,Qty,PriceLow,PriceHigh,InsufficientQty'.split(',')

def update2DB(table, datas):
    try:
        table.insert_many(datas)
    except:
        for d in datas:
            try:
                table.update_one(d, {'$set':d}, upsert=True)
            except:
                tmp = list(table.find({"Ticker":d['Ticker'], "Date":d['Date']}))
                if tmp:
                    # print(tmp)
                    d.update({"_id":tmp[0]['_id']})
                    table.update_one({"_id":d['_id']}, {'$set':d}, upsert=True)

def getBidFromTWSE(date):
    output = []
    if date < datetime(2005,1,19):
        return output
    dtStr = date.strftime("%Y%m%d")
    url = f'https://www.twse.com.tw/exchangeReport/BFIB8U?response=json&date={dtStr}&date2={dtStr}&stockNo=&_=1663313956018'
    js = crawl_json_data(url)
    if "OK" in js['stat']:
        cols = 'Date,Ticker,Name,Fin_Company,BidQty,BidPriceH,Qty,PriceLow,PriceHigh,InsufficientQty'.split(',')
        # print(js)
        
        data = js['data']
        for d in data:
            tmp = dict((k, v) for k, v in zip(cols, d))
            tmp['Date'] = date.strftime("%Y-%m-%d")
            output.append(tmp)
    return output

def getBidFromOTC(date):
    output = []
    dtStr = str(int(date.year-1911)) + date.strftime("/%m/%d")
    url = f'https://www.tpex.org.tw/web/stock/margin_trading/lend/lend_result.php?sd={dtStr}&ed={dtStr}&stkno=&_=1663314891562'
    js = crawl_json_data(url)
    if js['aaData']:
        # cols_chi = ["標借日期", "證券代號", "證券名稱", "證金公司", "標借數量", "最高標借單價", "得標數量", "
        data = js['aaData']
        for d in data:
            tmp = dict((k, v) for k, v in zip(cols, d))
            tmp['Date'] = date.strftime("%Y-%m-%d")
            output.append(tmp)
    return output

def main(date = datetime.today(), from_date = None):
    try:
        start_time = time.time()
        client = Mongo()
        schema = client['admin']
        table_name = 'Stock.Bid'
        collections = schema.list_collection_names()
        db_not_found = table_name not in collections
        table = schema[table_name]
        if all([db_not_found]):
            table.create_index([('Date', 1), ('Ticker', 1)], unique=True)
        else:
            cnt = table.count()
            if not all([cnt]):
                table.create_index([('Date', 1), ('Ticker', 1)], unique=True)
        last_date = table.distinct("Date")
        start_date = date
        if last_date:
            start_date = to_datetime(sorted(last_date)[-1]) + timedelta(1)
        else:
            start_date = datetime(2003,8,1)
        if from_date:
            start_date = from_date
        cnt = 0
        for dt in date_range(start_date, date):
            print(dt)
            tse_data = getBidFromTWSE(dt)
            otc_data = getBidFromTWSE(dt)
            output = tse_data+otc_data
            if output:
                update2DB(table, output)
            time.sleep(15)
            cnt+=1
            if cnt == 10:
                time.sleep(15)
                cnt = 0
        duration = time.time() - start_time
    except Exception as e:
        Tele().sendMessage(f'{_FileTitle} Failed', group='UpdateMessage')
        print(e)
    else:
        Tele().sendMessage(f'{_FileTitle} Success, cost {round(duration, 2)} seconds.', group='UpdateMessage')
    
if __name__ == '__main__':
    # main(from_date=datetime(2022,9,16))
    main()