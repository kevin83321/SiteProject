# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.03.02
# Update: Insert First Time
# Version: 1

from PyCasFunc import CassandraInsert
from PyDBFunc import Mongo
from datetime import datetime

def getOTCList():
    schema = Mongo()
    table = schema['TWSE.StockList']
    updateDate = sorted(list(table.distinct('UpdateDate')))[-1]
    datas = list(table.find({'UpdateDate':{'$eq':updateDate}, 
                        'AssetType':{'$in':['ETF', '股票']},
                        'Market':{'$eq':'上櫃'}}))
    asset_type = dict((x['Ticker'], x['AssetType'])  for x in datas)
    return [x['Ticker'] for x in datas], asset_type, updateDate

def getHistoricalData(latest=False):
    schema = Mongo()
    table = schema['TWSE.historicalPrice']
    otc_list, asset_type, updateDate = getOTCList()
    if latest:
        datas = list(table.find({'Ticker':{'$in':otc_list}, 'Date':{'$gte':updateDate}}))
    else: 
        datas = list(table.find({'Ticker':{'$in':otc_list}}))
    datas = [ChangeIntoCasForm(data, asset_type[data['Ticker']]) for data in datas]
    return datas
    
def ChangeIntoCasForm(data, asset_type):
    update_date, update_time = datetime.today().strftime('%Y/%m/%d %H:%M:%S').split(' ')
    
    return {
        'exchange': 'TW',
        'assets_type': asset_type,
        'symbol_code': data['Ticker'],
        'kline_period': '1440',
        'kline_datetime': data['Date'].replace('-', '/'),
        'close_price': data['Close'],
        'high_price': data['High'],
        'low_price': data['Low'],
        'open_price': data['Open'],
        'pkno': None,
        'trans_volume': data['Volume'],
        'update_date': update_date,
        'update_time': update_time,
        'update_user_id': 'Kevin',
    }
    
if __name__ == '__main__':
    datas = getHistoricalData()
    CassandraInsert(datas)