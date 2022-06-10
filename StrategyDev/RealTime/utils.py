
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
import numpy as np
from pymongo import MongoClient
from Config import mongo_setting
from Messenger import TelegramMessenger as tele
import os
from datetime import datetime, timedelta
from platform import system
if system() == 'Darwin':
    import matplotlib
    matplotlib.use("MacOSX")
import matplotlib.pyplot as plt
import mpl_finance as mpf
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mpl_ticker
import matplotlib.dates as mpl_dates
from Log.TransforException import GetException
from prettytable import PrettyTable

from matplotlib import colors as mcolors
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import TICKLEFT, TICKRIGHT, Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D
from itertools import product

from six.moves import xrange#, zip
from copy import deepcopy

from matplotlib.pylab import date2num # 导入日期到数值一一对应的转换工具
from matplotlib.font_manager import fontManager, FontProperties
ChineseFont = FontProperties([f.name for f in fontManager.ttflist if 'JhengHei' in f.name or 'Heiti' in f.name or 'Arial ' in f.name][0])

__updated__ = '2021-12-28 20:55:46'

td = datetime.today()
parent = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(parent):
    parent = os.getcwd()
    
fig_path = os.path.join(parent, 'ResultPlot', str(td.year).zfill(4), str(td.month).zfill(2), str(td.day).zfill(2))
if not os.path.isdir(fig_path):
    os.makedirs(fig_path)
    
record_path = os.path.join(parent, 'CummunicateRecord')
if not os.path.isdir(record_path):
    os.makedirs(record_path)

def saveRecommand(tickers, filename):
    lines = ','.join([td.strftime("%Y-%m-%d")]+tickers) + '\n'
    if '.txt' not in filename:
        filename += '.txt'
    with open(os.path.join(fig_path, filename), 'a', encoding='utf-8-sig') as f:
        f.writelines(lines)
        
def sendPhoto(text, fig_full_path):
    tele.sendPhoto(text, fig_full_path)
    
def sendMessage(text):
    tele.sendMessage(text)
    

def getclient(setting=None):
    if setting is None:
        setting = mongo_setting
    user = setting['user']
    pwd = setting['password']
    ip = setting['ip']
    port = setting['port']
    return MongoClient(f'mongodb://{user}:{pwd}@{ip}:{port}')
    

def getSchema(schema='TWSE', setting=None):
    client = getclient(setting)
    return client['admin'][schema]

def GetData(ticker, td = datetime.today(), years=1):
    # setup data
    schema = getSchema('TWSE')
    table = schema['historicalPrice']
    pre_3y = td + timedelta(-365*years)
    temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))).set_index('Date')
    return temp_df

def getDateBeforeTrade(td:datetime=None, adj_days=0):
    if td is None:
        td = datetime.now()
    # Check update Time
    if td <= td.replace(hour=5, minute=0, second=0):
        td += timedelta(-1)
    td += timedelta(days=-adj_days)
    print(td)
    if td.weekday() == 0:
        last = td + timedelta(-3)
    elif td.weekday() == 6:
        last = td + timedelta(-3)
        td += timedelta(-2)
    elif td.weekday() == 5:
        last = td + timedelta(-2)
        td += timedelta(-1)
    else:
        last = td + timedelta(-1)
        
    return td, last

def createRecommandTable(tickers, momentum:list=None, Industry:dict=None):
    try:
        table = PrettyTable()
        tickers = sorted(tickers)
        table.add_column('股票代號', tickers)
        if momentum:
            sorted_mom = dict([(ticker, f'{round(mom * 100, 2)} %') for ticker, mom in sorted(momentum, key=lambda x: x[1])[::-1] if ticker in tickers])
            moms = [sorted_mom[x] for x in tickers]
            table.add_column('動量', moms)
        if Industry:
            industry = [Industry[x] for x in tickers]
            table.add_column('產業', industry)
        table.align = 'r'
    except:
        print(GetException())
    else:
        return table
    
def sendResultTable(td, tickers, momentum=None, algo_num=1, expand_text='', Industry:dict=None):
    try:
        table = createRecommandTable(tickers, momentum, Industry)
        tdStr = td.strftime('%Y-%m-%d')
        text = f'{tdStr} \n'
        text += f'透過狗狗{algo_num}號\n'
        text += '計算出下一交易日可以關注的標的\n\n'
        text += table.get_string()
        text += '\n\n' + expand_text
        sendMessage(text)
    except:
        print(GetException())
        
def VolumeFilter(df, tickers, min_volume=None, min_ratio=None):
    selections = set()
    for ticker in tickers:
        temp = df[df.Ticker == ticker]
        gte_min_volume = gte_min_ratio = 1
        try:
            if min_ratio is not None:
                gte_min_ratio = temp.Volume[1] >= temp.Volume[0] * min_ratio
            if min_volume is not None:
                gte_min_volume = temp.Volume[1] > min_volume
            if all([gte_min_volume, gte_min_ratio]):
                selections.add(ticker)
        except:
            print(GetException())
            print(temp)
    return selections

def PriceFilter(df, tickers, max_price=None, min_price=None):
    selections = set()
    for ticker in tickers:
        temp = df[df.Ticker == ticker]
        gte_min_price = lte_max_price = 1
        try:
            if max_price is not None:
                lte_max_price = float(temp.Close[1]) <= max_price
            if min_price is not None:
                gte_min_price = min_price <= float(temp.Close[1])
            if all([gte_min_price, lte_max_price]):
                selections.add(ticker)
        except:
            print('Price Filter')
            print(temp)
    return selections

def Amplitude(df, num=100, critical=.04):
    try:
        last_date = df.index.unique()[-1]
        temp_df = df.loc[last_date, :]
        temp_df['Amplitude'] = (temp_df.High - temp_df.Low) / df.loc[df.index.unique()[0], :].Close.values
        temp_df = temp_df.sort_values('Amplitude', ascending=False)[:num]
    except Exception as e:
        print('Amplitude', e)
    else:
        return list(temp_df[temp_df.Amplitude >= critical].Ticker) # 
        
def Increase(df, tickers, num=100, top: bool=True):
    increases = []
    num = int(min(len(tickers), num) / 2)
    for ticker in tickers:
        temp = df[df.Ticker == ticker]
        try:
            ret = temp.Close.pct_change().fillna(0).sum()
            increases.append((ticker, ret))            
        except:
            pass
    sorted_increases = sorted(increases, key=lambda x: x[1])
    if top:
        return [x[0] for x in sorted_increases][-num:]
    else:
        return [x[0] for x in sorted_increases][:num]#  if x[1] >= 0.05

def totalValue(df, num = 100):
    try:
        last_date = df.index.unique()[-1]
        df = df.loc[last_date, :]
        df['TotalValue'] = df.Close * df.Volume
        df = df.sort_values('TotalValue')[-num:]
    except:
        pass
    else:
        return list(df.Ticker)        

def changedType(x):
    try:
        if '--' in x:
            return float('nan')
        if isinstance(x, str):
            return float(x.replace(',',''))
        return x
    except:
        return x
    
def Increase_filter(df):
    value_select = list(totalValue(df))
    amp_select = list(Amplitude(df))
    inc_select = list(Increase(df,amp_select))
    return list(set(value_select).intersection(inc_select))

def Decrease_filter(df):
    value_select = list(totalValue(df))
    amp_select = list(Amplitude(df))
    dec_select = list(Increase(df, amp_select, top=False))
    return list(set(value_select).intersection(dec_select))

def getStockList(schema):
    table = schema['StockList']
    updateDate = sorted(table.distinct('UpdateDate'))[-1]
    tickers = list(table.find({'UpdateDate':{'$eq':updateDate}, 'Industry':{"$ne":''}, 'Market':{'$in':['上市','上櫃']}}))
    listed = [x['Ticker'] for x in tickers if x['Market'] == '上市']
    otc = [x['Ticker'] for x in tickers if x['Market'] == '上櫃']
    return (listed, otc)

def parseRollingData(df, rolling):
    if rolling == "D": return df
    temp_data = df.resample(rolling).last()
    def Aggregate(arg):
        rolling, end_date, df = arg
        if rolling == 'M':
            start_date = datetime(end_date.year, end_date.month, 1)
        elif rolling == "W":
            start_date = end_date - timedelta(days=7)
        elif rolling == 'Q':
            start_date = datetime(end_date.year, end_date.month-2, 1)
        elif rolling == 'Y':
            start_date = datetime(end_date.year, 1, 1)
        date_range = pd.date_range(start_date, end_date)
        temp = df.loc[[x for x in df.index if x in date_range],:]
        if temp.empty: return
        temp_df = temp.loc[temp.index[-1], :]
        temp_df.Volume = temp.Volume.sum()
        temp_df.Open = temp.Open[0]
        temp_df.High = temp.High.max()
        temp_df.Low = temp.Low.min()
        return temp_df
    return pd.concat([x for x in list(map(Aggregate, product([rolling], temp_data.index, [df]))) if x is not None], axis=1).T

def crawlHotStocks():
    import requests
    from bs4 import BeautifulSoup
    tickers = []
    t = 'vol'
    for e in ['tse', 'otc']:
        url = f'https://tw.stock.yahoo.com/d/i/rank.php?t={t}&e={e}&n=100'

        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml") # 把原始碼做整理
        # 取得日期
        date = soup.select('table')[2].select('table')[0].select('td')[0].text[5:18].strip().replace(' ','').replace('/','_')
        # 取得排行名稱
        name = soup.select('table')[2].select('table')[0].select('td')[1].text.strip()
        soup_data = soup.select('table')[2].select('table')[1].select('td')
        
        # 取得表格內容
        for i in range(100):
            i *= 10
            tickers.append(soup_data[1 + i].text.strip().split(' ')[0])
    return tickers