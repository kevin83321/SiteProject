# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的股票的除權、息，分割，合併
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Version: 1

__updated__ = '2021-02-01 20:43:41'

from pandas import DataFrame, concat, date_range
from bs4 import BeautifulSoup as bs
import re, time, json, urllib.request, os
from datetime import timedelta, datetime
from modules import Tele, Mongo, crawl_json_data
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): 
    path = os.getcwd()
    
col_map = {'證券代號':'Ticker', 
           '證券名稱':'Name', 
           '成交股數':'Volume', 
           '成交筆數':'NumOfTransactions', 
           '成交金額':'Values', 
           '當日第一次成交價':'FirstPrice', 
           '當日最後一次成交價':'Close', 
           '成交價':'Close', 
           '當日最高價':'High', 
           '當日最低價':'Low', 
           '最後揭示買價':'LastBidPrice', 
           '最後揭示買量':'LastBidQty', 
           '最後揭示賣價':'LastAskPrice', 
           '最後揭示賣量':'LastAskQty'}

def changeTypes(k, v):
    k = col_map.get(k, k)
    if k in 'Ticker,Name'.split(','):
        return k, v
    if '-' not in v:
        v = float(v.replace(',',''))
    else:
        v = float('nan')
    return (k, v)        

def OddLot_Intraday(date):
    """
    盤中零股交易歷史資料
    """
    try:
        dateStr = date.strftime('%Y-%m-%d')
        url = f'https://www.twse.com.tw/exchangeReport/TWTC7U?response=json&date={dateStr.replace("-","")}&selectType=&_=1606553379802'
        js = crawl_json_data(url)
        columns = js['fields']
        datas = js['data']
        full_dict = []
        for data in datas:
            temp_data = dict(changeTypes(col, d) for col, d in zip(columns, data))
            temp_data.update({'Date':dateStr})
            full_dict.append(temp_data)
    except Exception as e:
        print('Intraday, Error : ',e)
    else:
        return full_dict

def OddLot_AfterHour(date):
    """
    盤後零股交易歷史資料
    """
    try:
        dateStr = date.strftime('%Y-%m-%d')
        url = f'https://www.twse.com.tw/exchangeReport/TWT53U?response=json&date={dateStr.replace("-","")}&selectType=&_=1606553422975'
        js = crawl_json_data(url)
        # print(js)
        columns = js['fields']
        datas = js['data']
        full_dict = []
        for data in datas:
            temp_data = dict(changeTypes(col, d) for col, d in zip(columns, data))
            temp_data.update({'Date':dateStr})
            full_dict.append(temp_data)
    except Exception as e:
        print('AfterHour, Error :',e)
    else:
        return full_dict

if __name__ == "__main__":
    # OddLot_AfterHour(datetime(2004, 12,24))
    # print()
    client = Mongo()
    schema = client['admin']
    table_intraday_name = 'TWSE.OddLot.Intraday'
    table_afterhour_name = 'TWSE.OddLot.AfterHour'
    collections = schema.collection_names()
    collections = schema.list_collection_names()
    intraday_not_found = table_intraday_name not in collections
    afterhour_not_found = table_afterhour_name not in collections
    intraday_table = schema[table_intraday_name]
    afterhour_table = schema[table_afterhour_name]
    if intraday_not_found:
        intraday_table.create_index([('Date', 1), ('Ticker', 1), ('Name', 1)], unique=True)
        intraday_start = datetime(2020,10,26)
    else:
        cnt = intraday_table.count_documents({})
        if cnt != 0:
            intraday_start = datetime.strptime(intraday_table.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
        else:
            intraday_start = datetime(2020,10,26)
        
    if afterhour_not_found:
        afterhour_table.create_index([('Date', 1), ('Ticker', 1), ('Name', 1)], unique=True)
        afterhour_start = datetime(2004,12,24)
    else:
        cnt = afterhour_table.count_documents({})
        if cnt != 0:
            afterhour_start = datetime.strptime(afterhour_table.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
        else:
            afterhour_start = datetime(2004,12,24)
        
    if intraday_start == afterhour_start: # db exists
        dates = date_range(intraday_start, datetime.today())
        print('DB exists.')
        for date in dates:
            print(f'crawl {date}')
            try:
                # crawl Intraday and insert to mongo
                Intraday_Odds = OddLot_Intraday(date)
                if Intraday_Odds is not None:
                    intraday_table.insert_many(Intraday_Odds)
            except:
                time.sleep(10)
                
            try:
                # crawl AfterHour and insert to mongo    
                AfterHour_Odds = OddLot_AfterHour(date)
                if AfterHour_Odds is not None:
                    afterhour_table.insert_many(AfterHour_Odds)
            except:
                time.sleep(10)
            time.sleep(5)
            
    else: #null db or haven't up to date
        dates = date_range(afterhour_start, datetime.today())
        print('First time for create DB or haven\'t up to date')
        for date in dates:
            print(f'crawl {date}')
            try:
                # crawl Intraday and insert to mongo
                AfterHour_Odds = OddLot_AfterHour(date)
                if AfterHour_Odds is not None:
                    afterhour_table.insert_many(AfterHour_Odds)
            except:
                time.sleep(10)            
                
            try:
                # crawl AfterHour and insert to mongo
                if date >= intraday_start:
                    Intraday_Odds = OddLot_Intraday(date)
                    if Intraday_Odds is not None:
                        intraday_table.insert_many(Intraday_Odds)
            except:
                time.sleep(10)
            time.sleep(5)

    # send finish message
    Tele().sendMessage('Update TWSE Odd Lot Success.', group='UpdateMessage')