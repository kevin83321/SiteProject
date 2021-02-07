#!/usr/bin/env python
# coding: utf-8
# 期交所歷史資料爬蟲
# 
# ref: https://raymond-investment.com/python-x-%e9%81%b8%e6%93%87%e6%ac%8a%ef%bd%9c%e9%81%b8%e6%93%87%e6%ac%8a%e5%9b%9e%e6%b8%ac/
# ## import modules

#%%
import os
parent = os.path.dirname(os.path.abspath(__file__))
# setup data path
optPath = os.path.join(parent, 'TAIFEX', 'Interday', 'Option')
if not os.path.isdir(optPath):
    os.makedirs(optPath)
futPath = os.path.join(parent, 'TAIFEX', 'Interday', 'Future')
if not os.path.isdir(futPath):
    os.makedirs(futPath)

import pandas as pd
import numpy as np
import time
from os import listdir
import sqlite3
from zipfile import ZipFile
import requests
from datetime import datetime , timedelta
from concurrent.futures import ThreadPoolExecutor
from modules import Tele, Mongo
from Log.TransforException import TransforException

#%%
## read historical data from TAIFEX
# Set Functions for process Data 

def parseFutureID(_id, ttm):
    try:
        if isinstance(_id, float):
            if np.isnan(_id):
                return '', ''
        y = ttm[:4]
        m = ttm[4:]

        if _id != 'MTX':
            capital_id = _id + m
            if _id in 'TF,TE'.split(','):
                _id = _id[-1] + 'X'
            m = list('ABCDEFGHIJKL')[int(m)-1]
            if len(_id) == 2:
                shioaji_id = _id + 'F' + m + y[-1]
            else:
                shioaji_id = _id + m + y[-1]
        else: #if (_id == 'MTX' and 'W' not in ttm) or
            if 'W' not in ttm:
                capital_id = _id + m
                m = list('ABCDEFGHIJKL')[int(m)-1]
                shioaji_id = 'MXF' + m + y[-1]
            else:
                m = m.split('W')
                capital_id = ''.join(['MX'] + m[::-1])
                m_code = list('ABCDEFGHIJKL')[int(m[0])-1]
                shioaji_id = 'MX' + m[-1] + m_code + y[-1]
        return capital_id, shioaji_id
    except:
        print(TransforException.GetException())
        print(_id, ttm)
    
def createBrokerID(data):
    try:
        ttm = data['Maturity'].strip()
        _id = data['Contract']
        if '/' not in ttm:
            capital_id, shioaji_id = parseFutureID(_id, ttm)
        else:
            ttm = ttm.split('/')
            capital1, _ = parseFutureID(_id, ttm[0])
            capital2, _ = parseFutureID(_id, ttm[1])
            if 'W' in ttm[0]:
                capital_id = '/'.join([capital1,capital2])
            else:
                capital_id = '/'.join([capital1,capital2[-2:]])
            shioaji_id = ''

        data.update({
            'TickerCapital':capital_id,
            'TickerShioaji':shioaji_id
        })
        return data
    except:
        print(TransforException.GetException())
        print(data)

def update_one(table, createIDFunc, d):
    try:
        if isinstance(d['Contract'], float):
            if np.isnan(d['Contract']) or d['Date'] is None:
                return
        d = createIDFunc(d)
        try:
            fut_table.update_one(d, {'$set':d}, upsert=True)
        except Exception as e:
            print(e)
    except Exception as e:
        print(TransforException.GetException())

def changeColNames(col):
    rename_map = {'Last':'Close', '%':'PctChange', 'Oi':'OI'}
    if 'month' in col.lower():
        return 'Maturity'
    if ' ' in col:
        col = col.split(' ')
    elif '_' in col:
        col = col.split('_')
    elif '/' in col:
        col = col.split('/')
    else:
        col = [col]
    col = [c.capitalize() for c in col]
    return rename_map.get(''.join(col), ''.join(col))

def parseDatetime(dt):
    try:
        return pd.to_datetime(dt).strftime('%Y-%m-%d')
    except:
        return np.nan

def createTickerOpt(data):
    try:
        ttm = data['Maturity']
        _id = data['Contract']
        if _id in 'TXO,TEO,TFO':
            strike = str(int(float(data['StrikePrice']))).replace('.', '').zfill(5)
        else:
            strike = str(float(data['StrikePrice'])*10).replace('.', '').zfill(5)
        c_p_map = {'Call':list('ABCDEFGHIJKL'), 'Put':list('MNOPQRSTUVWX')}
        y = ttm[:4]
        m = ttm[4:]
        
        if 'W' not in ttm:
            c_p_code = c_p_map[data['CallPut']][int(m)-1]
            ticker = _id + strike + c_p_code + y[-1]
        else:
            w = m[-1]
            c_p_code = c_p_map[data['CallPut']][int(m[:2])-1]
            ticker = _id[:-1] + w + strike + c_p_code + y[-1]
        
        data.update({
            'TickerCapital':ticker,
            'TickerShioaji':ticker
        })
    except:
        print(TransforException.GetException())
    else:   
        return data

def parallel_update_data(createFunc, df):
    with ThreadPoolExecutor(20) as executor:
        exes = [executor.submit(createFunc, d) for d in list(df.T.to_dict().values())]
        datas = [exe.result() for exe in exes]
        datas = [d for d in datas if d is not None]
    return datas

def parallel_update(table, createFunc, df):
    try:
        table.insert_many(parallel_update_data(createFunc, df))
    except:
        with ThreadPoolExecutor(20) as executor:
            exes = [executor.submit(update_one, table, createFunc, d) for d in list(df.T.to_dict().values())]
            [exe.result() for exe in exes]
        
###################################
# # Crawl Daily Future Data (Month)
###################################
def Futures_Data_Daily(lastDate):
    td = datetime.now()
    start_date = datetime.strptime(lastDate, '%Y-%m-%d')
    end_date = min(start_date + timedelta(days=30), td)
    datas = []
    print(start_date, end_date, td)
    while start_date <= td and end_date <= td:
        url = f"""https://www.taifex.com.tw/enl/eng3/futDataDown?down_type=1&queryStartDate={start_date.strftime('%Y/%m/%d')}&queryEndDate={end_date.strftime('%Y/%m/%d')}&commodity_id=all"""
        r = requests.get(url)
        data_parsed = [d.split(',') for d in r.content.decode().split('\r\n')]
        full_data = []
        for data in data_parsed[1:]:
            temp_dict = dict((changeColNames(data_parsed[0][i]), d) for i, d in enumerate(data[:-2]))
            full_data.append(temp_dict)
        if full_data:
            datas.extend(full_data)
        start_date = end_date
        end_date = start_date + timedelta(days=30)
    
    df =  pd.DataFrame(datas).replace('-', np.nan).dropna(how='all', axis=0)
    for col in list(df.columns):
        if col not in 'Date,Contract,Maturity,PctChange,TradingSession,TradingHalt'.split(','):
            try:
                df[col] = df[col].astype(float)
            except:
                pass
    return df
    
def Options_Data_Daily(lastDate):
    td = datetime.now()
    start_date = datetime.strptime(lastDate, '%Y-%m-%d')
    end_date = min(start_date + timedelta(days=30), td)
    datas = []
    while start_date <= td and end_date <= td:
        url = f"""https://www.taifex.com.tw/enl/eng3/optDataDown?down_type=1&queryStartDate={start_date.strftime('%Y/%m/%d')}&queryEndDate={end_date.strftime('%Y/%m/%d')}&commodity_id=all"""
        r = requests.get(url)
        try:
            data = r.content.decode()
        except:
            data = r.content.decode('big5')
        data_parsed = [d.split(',') for d in data.split('\r\n')]
        full_data = []
        for data in data_parsed[1:]:
            temp_dict = dict((changeColNames(data_parsed[0][i]), d) for i, d in enumerate(data[:-1]))
            full_data.append(temp_dict)
        datas.extend(full_data)
        start_date = end_date
        end_date = start_date + timedelta(days=30)
        time.sleep(1)
    df = pd.DataFrame(datas).replace('-',np.nan).dropna(how='all', axis=0)
    df.Date = df.Date.apply(parseDatetime)
    for col in list(df.columns):
        if col not in 'Date,Contract,StrikePrice,CallPut,Maturity,PctChange,TradingSession,TradingHalt'.split(','):
            try:
                df[col] = df[col].astype(float)
            except:
                pass
    return df
#######################################
# # Crawl Historical Data (Year)
#######################################

def Futures_Data(LastYear):
    Years = np.arange(1998,LastYear + 1)
    for Year in Years:
        url = 'https://www.taifex.com.tw/enl/eng3/futDataDown?down_type=2&his_year=' + str(Year)
        r = requests.get(url)
        open(os.path.join(futPath, str(Year) + '.zip'),'wb').write(r.content)

def Options_Data(LastYear):
    Years = np.arange(2001,LastYear + 1)
    for Year in Years:
        url = 'https://www.taifex.com.tw/enl/eng3/optDataDown?down_type=2&his_year=' + str(Year)
        r = requests.get(url)
        open(os.path.join(optPath, str(Year) + '.zip'),'wb').write(r.content)     
        
###################################
# # Read Yearly Data From Files
###################################

def Futures(File_Name):
    try:
        df = pd.read_csv(os.path.join(futPath, str(File_Name)),index_col = False, low_memory=False).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
        df.columns = [changeColNames(col) for col in df.columns]
        for each in df.columns:
            if each not in 'Date,Maturity,Contract'.split(','):
                try:
                    df[each] = df[each].astype(float)
                except:
                    pass
        df.Maturity = df.Maturity.astype(str)

        df['Date'] = df['Date'].apply(parseDatetime)#lambda x: x.replace('/', '-'))    
        print(str(File_Name) + ' created successfully.')
        return df
    except:
        pass

def Futures_Before2017(File_Name):
    try:
        df = pd.read_csv(os.path.join(futPath, str(File_Name)),index_col = False, low_memory=False).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
        df.columns = [changeColNames(col) for col in df.columns]

        for each in df.columns:
            if each not in 'Date,Maturity,Contract'.split(','):
                try:
                    df[each] = df[each].astype(float)
                except:
                    pass
        df.Maturity = df.Maturity.astype(str)
        df['Date'] = df['Date'].apply(parseDatetime)#lambda x: x.replace('/', '-'))    
        print(str(File_Name) + ' created successfully.')
        return df
    except:
        pass

def Futures_Before2006(File_Name):
    try:
        df = pd.read_csv(os.path.join(futPath, str(File_Name)),index_col = False, low_memory=False).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
        df.columns = [changeColNames(col) for col in df.columns]
        for each in df.columns:
            if each not in 'Date,Maturity,Contract'.split(','):
                try:
                    df[each] = df[each].astype(float)
                except:
                    pass
        df.Maturity = df.Maturity.astype(str)
        df['Date'] = df['Date'].apply(parseDatetime)#lambda x: x.replace('/', '-'))    
        print(str(File_Name) + ' created successfully.')
        return df
    except:
        pass

def Options(File_Name):
    df = pd.read_csv(os.path.join(optPath, str(File_Name)),index_col = False).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
    df.columns = [changeColNames(col) for col in df.columns]
    
    for each in df.columns:
        if each not in 'Date,Maturity,Contract,CallPut,StrikePrice'.split(','):
            try:
                df[each] = df[each].astype(float)
            except:
                pass
    df.Maturity = df.Maturity.astype(str)
    df['Date'] = df['Date'].apply(parseDatetime)
    print(str(File_Name) + ' created successfully.')
    return df
    
def Options_multiFiles(File_Name):
    zip_file = ZipFile(os.path.join(optPath, File_Name))
    files_in_zip = [f.filename for f in zip_file.filelist if '.csv' in f.filename]
    dfs = []
    for f in files_in_zip:
        df = pd.read_csv(zip_file.open(f),index_col = False, error_bad_lines=False).replace('-', np.nan).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
        df.columns = [changeColNames(col) for col in df.columns]

        for each in df.columns:
            if each not in 'Date,Maturity,Contract,CallPut,StrikePrice'.split(','):
                try:
                    df[each] = df[each].astype(float)
                except:
                    pass
        df.Maturity = df.Maturity.astype(str)
        df['Date'] = df['Date'].apply(parseDatetime)
        print(str(f) + ' in ' + str(File_Name) + ' created successfully.')
        dfs.extend(list(df.dropna(how='all', axis=0).T.to_dict().values()))
    return pd.DataFrame(dfs)
    
def Options_Before2015(File_Name):
    df = pd.read_csv(os.path.join(optPath, str(File_Name)),index_col = False).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
    df.columns = [changeColNames(col) for col in df.columns]
    
    for each in df.columns:
        if each not in 'Date,Maturity,Contract,CallPut,StrikePrice'.split(','):
            try:
                df[each] = df[each].astype(float)
            except:
                pass
    df.Maturity = df.Maturity.astype(str)
    df['Date'] = df['Date'].apply(parseDatetime)
    print(str(File_Name) + ' created successfully.')
    return df

def Options_Before2010(File_Name):
    df = pd.read_csv(os.path.join(optPath, str(File_Name)),index_col = False).replace('-', np.nan).replace('None', np.nan).dropna(how='all')
    df.columns = [changeColNames(col) for col in df.columns]
    
    for each in df.columns:
        if each not in 'Date,Maturity,Contract,CallPut,StrikePrice'.split(','):
            try:
                df[each] = df[each].astype(float)
            except:
                pass
    df.Maturity = df.Maturity.astype(str)
    df['Date'] = df['Date'].apply(parseDatetime)
    print(str(File_Name) + ' created successfully.')
    return df

if __name__ == '__main__':
    ########################
    # Setup database
    ########################
    
    # Connect to Mongo
    client = Mongo()
    schema = client['admin']
    collections = schema.collection_names()
    fut_table_name = 'TAIFEX.Interday.Future'
    opt_table_name = 'TAIFEX.Interday.Option'
    td = datetime.now()
    LastYear = td.year - 1
    first_fut = False
    first_opt = False
    
    # Setup Interday Future DB
    fut_table = schema[fut_table_name]
    first_fut = fut_table_name not in collections
    cnt = schema[fut_table_name].count()
    first_fut = cnt == 0
    if first_fut: # if db not exist or db is empty
        fut_table.create_index([('Date',1), ('Contract', 1), ('Maturity', 1)])
        Futures_Data(LastYear)
    
    # Setup Interday Option DB
    opt_table = schema[opt_table_name]
    first_opt = opt_table_name not in collections
    cnt = schema[opt_table_name].count()
    first_opt = cnt == 0
    if first_opt: # if db not exist or db is empty
        opt_table.create_index([('Date',1), ('Contract', 1), ('Maturity', 1), ('CallPut', 1)])
        Options_Data(LastYear)
    
    ###############################
    # Insert historical data Yearly
    ###############################
    # Yearly Data of Future
    if first_fut:
        Futures_Files = sorted(listdir(futPath))
        for Name in Futures_Files:
            if '.zip' not in Name: continue
            try:
                df = Futures(Name)
            except:
                try:
                    df = Futures_Before2017(Name)
                except:
                    df = Futures_Before2006(Name)
            parallel_update(fut_table, createBrokerID, df)
            time.sleep(1)

    # Yearly Data of Option
    if first_opt:
        Options_Files = sorted(listdir(optPath))
        for Name in Options_Files:
            if '.zip' not in Name: continue
            print('Option', Name)
            try:
                df = Options(Name)
            except:
                try:
                    df = Options_Before2015(Name)
                except:
                    try:
                        df = Options_Before2010(Name)
                    except:
                        df = Options_multiFiles(Name)
            parallel_update(opt_table, createTickerOpt, df)
            time.sleep(1)
        
    fut_lastDate = sorted([parseDatetime(x) for x in fut_table.distinct('Date') if x is not None])[-1]
    df = Futures_Data_Daily(fut_lastDate)
    parallel_update(fut_table, createBrokerID, df)
    
    opt_lastDate = sorted([parseDatetime(x) for x in opt_table.distinct('Date') if x is not None])[-1]
    df = Options_Data_Daily(opt_lastDate)
    parallel_update(opt_table, createTickerOpt, df)

    Tele().sendMessage(f'盤後爬取期交所,所有期貨收盤價成功', group='UpdateMessage')