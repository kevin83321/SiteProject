# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
# 爬取所有上市上櫃的股票交易日資料
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Update: add log write into cmd
# Version: 1

__updated__ = '2022-09-12 09:30:57'

from pandas import DataFrame, date_range, read_csv
from datetime import timedelta, datetime
import os
import time
import re
from modules import Tele, Mongo, crawl_json_data
from Log import TransforException

# setup path
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path):
    path = os.getcwd()
tsepath = os.path.join(path, 'TSE')
if not os.path.isdir(tsepath):
    os.makedirs(tsepath)
otcpath = os.path.join(path, 'OTC')
if not os.path.isdir(otcpath):
    os.makedirs(otcpath)


def update_data_dict(d):
    if 'Index' in d:
        del d['Index']
    delete_k = []
    for key in d.keys():
        if re.match(r'_[0-9]*', key):
            delete_k.append(key)
    for key in delete_k:
        d.pop(key)
    d['Adj Close'] = d['Close']
    return d

def changeToFloat(x):
    """
    將文字資料做轉換，補上NA
    以及去除數字較大帶有逗點的狀況
    """
    try:
        if isinstance(x, str):
            if '--' in x:
                return float('nan')
            if "X" in x:
                return float('nan')
        return float(str(x).replace(',',''))
    except:
        return x

def TSE_HistoricalPrice(i):
    output = []
    try:
        date = i.strftime('%Y%m%d')
        url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=' + \
            date + '&type=ALLBUT0999&_=1553846233285'

        js = crawl_json_data(url)
        # print(js)
        # os._exit(0)
        if 'data9' in js:
            data = js['data9']
        else:
            data = js['data8']
        for k in range(len(data)):
            o,h,l,c = [changeToFloat(x.replace(',','')) for x in data[k][5:9]]
            output.append(update_data_dict({
                'Date':i.strftime('%Y-%m-%d'),
                'Ticker':data[k][0],
                'Open':o,
                'High':h,
                'Low':l,
                'Close':c,
                'Volume':int(changeToFloat(data[k][2].replace(',',''))),
                'Value':int(changeToFloat(data[k][4].replace(',',''))),
            }))
    except Exception as e:
        print(e)
        pass
    return output


def OTC_HistoricalPrice(i):
    output = []
    try:
        date = '/'.join([str(i.year - 1911), i.strftime('%m/%d')])
        url = 'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d=' + \
            date + '&se=EW&_=1553850502415'
        js = crawl_json_data(url)
        data = js["aaData"]
        for k in range(len(data)):
            o,h,l,c = [changeToFloat(x.replace(',','')) for x in data[k][4:7]+data[k][2:3]]
            volume = int(changeToFloat(data[k][7].replace(',','')))
            value = int(changeToFloat(data[k][8].replace(',','')))
            # if i >= datetime(2020,7,24):
            #     volume = int(changeToFloat(data[k][7].replace(',','')))
            output.append(update_data_dict({
                'Date':i.strftime("%Y-%m-%d"),
                'Ticker':data[k][0],
                'Open':o,
                'High':h,
                'Low':l,
                'Close':c,
                'Volume':volume,
                "Value":value
            }))
    except Exception as e:
        print(e)
        pass
    return output

def Crawl_TWSE(date, table=None, update= False):
    try:
        # crawl tse daily data
        # 判斷是否曾經爬取過這一天的資料
        # 如果有的話則讀取本地資料
        islocal = False
        if os.path.isfile(os.path.join(
                tsepath, f"{date.strftime('%Y-%m-%d')}.txt")) and not update: 
            df_tse = read_csv(os.path.join(
                tsepath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t')
            data_tse = [update_data_dict(x) for x in list(df_tse.T.to_dict().values())]
            islocal = True
        else: # 如果沒有的話才進入證交所爬取資料
            data_tse = TSE_HistoricalPrice(date)

        # 確認是否有取得我們要的資料
        # 有資料才進行存檔與放入資料庫的動作
        if data_tse:
            DataFrame(data_tse).to_csv(os.path.join(
                tsepath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t', index=None, float_format='%g')
            if table:
                insert_data(table, data_tse)
        print(f'Update {date} Historical Price of tse success')
    except Exception as e:
        print(TransforException.GetException())
        # print('tse',e)
    else:
        return islocal
        
def Crawl_TPEX(date, table=None, update=False):
    try:
        islocal = False
        if date >= datetime(2007,1,2): # 上櫃股票的資料比較晚才有
            # crawl otc daily data
            # 判斷是否曾經爬取過這一天的資料
            # 如果有的話則讀取本地資料
            if os.path.isfile(os.path.join(
                    otcpath, f"{date.strftime('%Y-%m-%d')}.txt")) and not update:
                df_otc = read_csv(os.path.join(
                    otcpath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t')
                data_otc = [update_data_dict(x) for x in list(df_otc.T.to_dict().values())]
                islocal = True
            else:
                data_otc = OTC_HistoricalPrice(date)

            # 確認是否有取得我們要的資料
            # 有資料才進行存檔與放入資料庫的動作
            if data_otc:
                DataFrame(data_otc).to_csv(os.path.join(
                    otcpath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t', index=None, float_format='%g')
                if table:
                    insert_data(table, data_otc)
            print(f'Update {date} Historical Price of otc success')
    except Exception as e:
        print(TransforException.GetException())
        # print('otc',e)
    return islocal

def insert_data(table, data):
    try:
        table.insert_many(data)
    except:
        try:
            exists_ids = dict((x['Ticker'], x['_id']) for x in table.find({"Date":data[0]['Date']}))
            # print(exists_ids)
            for d in data:
                d.update({'_id': exists_ids[d['Ticker']]})
                update_one(table, d)
        except:
            print(TransforException.GetException())
            # table.update_one({"_id":d['_id'], })

def update_one(table, x): 
    try:
        table.update_one({'_id':x['_id']}, {'$set':x}, upsert=True)
    except KeyboardInterrupt:
        os._exit(0)
    except Exception as e:
        print(TransforException.GetException())
        pass

def main(startFrom = None, update=False):
    try:
        # print('create mongo connection')
        client = Mongo()
        schema = client['admin']
        # db_name = 'TWSE.HistoricalPrice' # 可自行更換資料庫(table)名稱
        db_name = 'TWSE.historicalPrice' # 可自行更換資料庫(table)名稱
        # print('get collections')
        collections = schema.list_collection_names()
        # print(collections, db_name in collections)
        if db_name in collections: # 資料庫存在
            table = schema[db_name]
            # tabel.count_documents
            nums = table.count()#_documents({})
            if not nums: # 資料庫沒有資料，所以進行完整的建立, 取資料公告的第一天
                table.create_index([('Date', 1), ('Ticker', 1)], unique=True)
                start_date = datetime(2004,2,11) # 此日期為證交所公告最早的日期 # 2004-2-11
            else: # 資料庫有資料，取上次更新的最後一天做為起始日期
                # print('get Exists Dates')
                start_date = datetime.strptime(sorted(list(table.distinct('Date')))[-1], '%Y-%m-%d') + timedelta(1)
                # print('start date:', start_date)
        else: # 資料庫不存在, 所以進行完整的建立, 取資料公告的第一天
            table = schema[db_name]
            table.create_index([('Date', 1), ('Ticker', 1)], unique=True)
            start_date = datetime(2004,2,11) # 此日期為證交所公告最早的日期 # 2004-2-11
        end_date = datetime.today() # 最後一日皆設定開啟的當日
        # start_date = datetime(2004,2,11)
        # end_date = datetime(2021,12,31)
        
        dates = date_range(start_date, end_date)
        if startFrom:
            dates = date_range(startFrom, end_date)
        print(start_date, end_date)
        for date in dates:
            print(date)
            tse_local = Crawl_TWSE(date, table, update)
            otc_local = Crawl_TPEX(date, table, update)
            if date < datetime(2007,1,2):
                if not tse_local:
                    time.sleep(5)
            else:
                if not all([tse_local, otc_local]):
                    time.sleep(5)
        # Tele().sendMessage('Update Stock Historical Price success', group='UpdateMessage')
    except:
        Tele().sendMessage(f'Update Stock Historical Price failed with Error: \n\n{TransforException.GetException()}', group='UpdateMessage')
        # print("Main Loop Error : ",e)
    else:
        Tele().sendMessage('Update Stock Historical Price success', group='UpdateMessage')

if __name__ == "__main__":
    # main(datetime(2015,1,27), True)
    main()