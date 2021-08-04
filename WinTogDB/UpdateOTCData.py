# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.03.02
# Update: Insert First Time
# Version: 1

__updated__ = '2021-07-15 01:39:33'

from PyCasFunc import CassandraInsert
from PyDBFunc import Mongo
from datetime import datetime, timedelta
from LineNotify import WintogLineNotify
import requests

header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'upgrade-insecure-requests': '1'}

def crawl_json_data(url):
    res = requests.get(url, headers=header)
    return res.json()

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
    try:
        return float(str(x).replace(',',''))
    except:
        return x

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
            # if i >= datetime(2020,7,24):
            #     volume = int(changeToFloat(data[k][7].replace(',','')))
            output.append(ChangeIntoCasForm(update_data_dict({
                'Date':i.strftime("%Y-%m-%d"),
                'Ticker':data[k][0],
                'Open':o,
                'High':h,
                'Low':l,
                'Close':c,
                'Volume':volume,
            })))
    except Exception as e:
        print(e)
        pass
    return output

def getOTCList():
    schema = Mongo()
    table = schema['TWSE.StockList']
    updateDate = sorted(list(table.distinct('UpdateDate')))[-1]
    datas = list(table.find({'UpdateDate':{'$eq':updateDate}, 
                        'AssetType':{'$in':['ETF', '股票']},
                        'Market':{'$eq':'上櫃'}}))
    asset_type = dict((x['Ticker'].strip(), x['AssetType'])  for x in datas)
    return datas, asset_type, updateDate

def getHistoricalData(latest=False, dateStr:str=None):
    schema = Mongo()
    table = schema['TWSE.historicalPrice']
    temp_datas, asset_type, updateDate = getOTCList()
    otc_list = [x['Ticker'] for x in temp_datas]
    if latest:
        datas = list(table.find({'Ticker':{'$in':otc_list}, 'Date':{'$gte':updateDate}}))
    elif dateStr:
        datas = list(table.find({'Ticker':{'$in':otc_list}, 'Date':{'$gte':dateStr}}))
    else: 
        datas = list(table.find({'Ticker':{'$in':otc_list}, 'Date':{'$gte':'2013-12-01'}}))
    datas = [ChangeIntoCasForm(data, asset_type[data['Ticker']]) for data in datas]
    return datas
    
def ChangeIntoCasForm(data, asset_type):
    update_date, update_time = datetime.today().strftime('%Y/%m/%d %H:%M:%S').split(' ')
    
    return {
        'exchange': 'TW',
        'assets_type': 'Stock' if asset_type == '股票' else 'ETF',
        'symbol_code': data['Ticker'],
        'kline_period': '1440',
        'kline_datetime': data['Date'].replace('-', '/'),
        'close_price': str(data['Close']),
        'high_price': str(data['High']),
        'low_price': str(data['Low']),
        'open_price': str(data['Open']),
        'pkno': None,
        'trans_volume': str(data['Volume']),
        'update_date': update_date,
        'update_time': update_time,
        'update_user_id': 'Kevin',
    }
    
def Update(dt=datetime.today()):
    start_date = datetime.strptime(dt, "%Y-%m-%d") if isinstance(dt, str) else dt
    end_date = datetime.today()
    i = 0
    while 1:
        date = start_date + timedelta(i)
        try:
            dateStr = date.strftime("%Y-%m-%d")
            datas = getHistoricalData(dateStr=dateStr)
            num = len(datas)
            CassandraInsert(datas=datas)
        except:
            pass
        else:
            WintogLineNotify(f'[MarketApi 更新台灣上櫃股票 {dateStr} 價格完成] 筆數: {num}')
        i += 1
        if date > end_date:
            break


if __name__ == '__main__':
    Update()