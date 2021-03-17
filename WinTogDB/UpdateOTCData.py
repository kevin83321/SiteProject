# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.03.02
# Update: Insert First Time
# Version: 1

__updated__ = '2021-03-13 10:37:46'

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
    asset_type = dict((x['Ticker'].strip(), x['AssetType'])  for x in datas)
    return datas, asset_type, updateDate

def getHistoricalData(latest=False):
    schema = Mongo()
    table = schema['TWSE.historicalPrice']
    temp_datas, asset_type, updateDate = getOTCList()
    otc_list = [x['Ticker'] for x in temp_datas]
    if latest:
        datas = list(table.find({'Ticker':{'$in':otc_list}, 'Date':{'$gte':updateDate}}))
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
    
if __name__ == '__main__':
    datas = getHistoricalData(True)
    # datas = [dict(exchange='TW', assets_type='Stock', symbol_code='1336', kline_period='1440', kline_datetime='2021/02/24', close_price='625.00', high_price='636.00', low_price='625.00', open_price='627.00', pkno=None, trans_volume='69675637', update_date='2021/02/24', update_prog_cd='MarketApi.FormMarketApi', update_time='15:12:17', update_user_id='Test')]
    CassandraInsert(datas=datas)