import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import time
from zipfile import ZipFile
import os
import re
from pymongo import MongoClient
from io import StringIO
from selenium import webdriver
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
from itertools import product
import json
chrome = ChromeDriverManager().install()

parent = os.path.dirname(os.path.abspath(__file__))
savePath = os.path.join(parent, 'balace_sheet')
if not os.path.isdir(savePath):
    os.makedirs(savePath)
filledPath = os.path.join(parent, 'filled_data')
if not os.path.isdir(filledPath):
    os.makedirs(filledPath)
    
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def final_publish_date(year):
    return  [datetime(year, 5, 15),
                datetime(year, 8, 14),
                datetime(year, 11, 14),
                datetime(year+1, 3, 31)]

def parse_balance_sheet_html(soup):
    balance_sheet = soup.find_all('table')[0]
    balance_sheet_dict = {'英文名稱(GAAP)':'Balance Sheet',
                          '英文名稱(IFRS)':'Statement of Financial Position'}
    
    for tr in balance_sheet.find_all('tr')[2:]:
        tds = [td.text.strip().replace(',', '').replace('\u3000','') for td in tr.find_all('td')]
        span = re.search(r'[a-z]+',tds[1], re.I).span()
        Eng_start = span[0]
        chinese = tds[1][:Eng_start]
        Eng = tds[1][Eng_start:]
        if tds[2] != '':
            if '(' in tds[2]:
                value = '-' + tds[2].replace('(', '').replace(')', '')
            else:
                value = tds[2].replace('(', '').replace(')', '')
            try:
                value = int(value)
            except:
                value = float(value)
            balance_sheet_dict.update({
                chinese:{
                '英文名稱':Eng,
                '科目代號':tds[0],
                'Value':value}
            })
    return balance_sheet_dict
    
def parse_income_sheet_html(soup):
    income_sheet = soup.find_all('table')[1]
    income_sheet_dict = {'英文名稱(GAAP)':'Income Statement',
                         '英文名稱(IFRS)':'Statement of Comprehensive Income'}
    
    for tr in income_sheet.find_all('tr')[2:]:
        tds = [td.text.strip().replace(',', '').replace('\u3000','') for td in tr.find_all('td')]
        span = re.search(r'[a-z]+',tds[1], re.I).span()
        Eng_start = span[0]
        chinese = tds[1][:Eng_start]
        Eng = tds[1][Eng_start:]
        if tds[2] != '':
            if '(' in tds[2]:
                value = '-' + tds[2].replace('(', '').replace(')', '')
            else:
                value = tds[2].replace('(', '').replace(')', '')
            try:
                value = int(value)
            except:
                value = float(value)
            
            income_sheet_dict.update({
                chinese:{
                '英文名稱':Eng,
                '科目代號':tds[0],
                'Value':value}
            })
    return income_sheet_dict

def parse_cash_flow_sheet_html(soup):
    cash_flow = soup.find_all('table')[2]
    cash_flow_dict = {'英文名稱(GAAP)':'Cash Flow Statement',
                      '英文名稱(IFRS)':'Statement of Cash Flows'}
    
    try:
        for tr in cash_flow.find_all('tr')[2:]:
            tds = [td.text.strip().replace(',', '').replace('\u3000','') for td in tr.find_all('td')]
            span = re.search(r'[a-z]+',tds[1], re.I).span()
            Eng_start = span[0]
            chinese = tds[1][:Eng_start]
            Eng = tds[1][Eng_start:]
            if tds[2] != '':
                if '(' in tds[2]:
                    value = '-' + tds[2].replace('(', '').replace(')', '')
                else:
                    value = tds[2].replace('(', '').replace(')', '')
                try:
                    value = int(value)
                except:
                    value = float(value)
                cash_flow_dict.update({
                    chinese:{
                    '英文名稱':Eng,
                    '科目代號':tds[0],
                    'Value':value}
                })
    except:
        return None
    else:
        return cash_flow_dict

def crawl_balance_sheet_zip(year=2019, season=1):
    if not os.path.isfile(os.path.join(savePath, f'{year}Q{season}.zip')):
        url = f'https://mops.twse.com.tw/server-java/FileDownLoad?step=9&fileName=tifrs-{year}Q{season}.zip&filePath=/home/html/nas/ifrs/{year}/'
        response = requests.get(url, headers=headers, timeout=30)
        open(os.path.join(savePath, f'{year}Q{season}.zip'),'wb').write(response.content)
    
def read_data_from_file(year=2019, season=1):
    if year < 2019:
        return crawl_data_before_2019(year, season)
    zip_file = ZipFile(os.path.join(savePath, f'{year}Q{season}.zip'))
    files_in_zip = [f.filename for f in zip_file.filelist if '.html' in f.filename]
    datas = []
    targetPath = os.path.join(filledPath, f'{year}Q{season}')
    if not os.path.isdir(targetPath):
        os.makedirs(targetPath)
        
    for f in files_in_zip:        
        ticker = f.split('-')[5]
        print(ticker, year, season)
        if os.path.isfile(os.path.join(targetPath, f'{ticker}.json')):
            with open(os.path.join(targetPath, f'{ticker}.json'), 'r') as f:
                temp = json.load(f)
        else:
            soup = bs(zip_file.open(f), 'lxml')
            balance_dict = parse_balance_sheet_html(soup)

            income_dict = parse_income_sheet_html(soup)

            cash_flow_dict = parse_cash_flow_sheet_html(soup)
            
            temp = {
                'Ticker':ticker,
                'Year':str(year),
                'Quarter':str(season),
                '資產負債表':balance_dict,
                '綜合損益表':income_dict,
                '現金流量表':cash_flow_dict,
                'updateDate':datetime.today().strftime('%Y-%m-%d')
            }
            with open(os.path.join(targetPath, f'{ticker}.json'), 'w') as f:
                json.dump(temp, f)
        datas.append(temp)
    return datas

def crawl_web_html_before_2019_with_selenium(ticker, year, season):
    driver = webdriver.Chrome(chrome)
    url = f'https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID={ticker}&SYEAR={year}&SSEASON={season}&REPORT_ID=C'
    driver.get(url)
    time.sleep(3)
    source = driver.page_source
    try:
        driver.close()
    except:
        driver.quit()
    return bs(source, 'lxml')
    
def crawl_data_before_2019(year=2013, season=1):
    tickers = read_data_from_file_before_2019(year, season)
    datas = []
    targetPath = os.path.join(filledPath, f'{year}Q{season}')
    if not os.path.isdir(targetPath):
        os.makedirs(targetPath)
    for ticker in tickers:
        print(ticker, year, season)
        if os.path.isfile(os.path.join(targetPath, f'{ticker}.json')):
            with open(os.path.join(targetPath, f'{ticker}.json'), 'r') as f:
                temp = json.load(f)
        else:
            cnt = 0
            while cnt <= 5:
                try:
                    soup = crawl_web_html_before_2019_with_selenium(ticker, year, season)
                except exceptions.WebDriverException:
                    continue
                if soup is not None:
                    tables = soup.find_all('table')
                    
                    balance_dict = None
                    if len(tables) > 1:
                        balance_dict = parse_balance_sheet_web_html(tables)
                    income_dict = None
                    if len(tables) > 2:
                        income_dict = parse_income_sheet_web_html(tables)
                    cash_flow_dict = None
                    if len(tables) > 3:
                        cash_flow_dict = parse_cash_flow_sheet_web_html(tables)
                    temp = {
                        'Ticker':ticker,
                        'Year':str(year),
                        'Quarter':str(season),
                        '資產負債表':balance_dict,
                        '綜合損益表':income_dict,
                        '現金流量表':cash_flow_dict,
                        'updateDate':datetime.today().strftime('%Y-%m-%d')
                    }
                    with open(os.path.join(targetPath, f'{ticker}.json'), 'w') as f:
                        json.dump(temp, f)
                    time.sleep(5)
                    break
                cnt += 1
                time.sleep(5)
        datas.append(temp)
    return datas
            
def parse_balance_sheet_web_html(tables):
    table = tables[1]
    balance_sheet_dict = {'英文名稱(GAAP)':'Balance Sheet',
                          '英文名稱(IFRS)':'Statement of Financial Position'}
    
    for tr in table.find_all('tr'):
        tds = [td.text.strip().replace(',', '') for td in tr.find_all('td')]
        try:
            if tds[1] != '':
                chinese = tds[0]
                try:
                    value = int(tds[1])
                except:
                    value = float(tds[1])
                balance_sheet_dict.update({
                    chinese:{
                        '英文名稱':'',
                        '科目代號':'',
                        'Value':value
                    }
                })
        except:
            print(tr)
            print(tds)
    return balance_sheet_dict
            
def parse_income_sheet_web_html(tables):
    table = tables[2]
    income_sheet_dict = {'英文名稱(GAAP)':'Income Statement',
                         '英文名稱(IFRS)':'Statement of Comprehensive Income'}
    
    for tr in table.find_all('tr'):
        tds = [td.text.strip().replace(',', '') for td in tr.find_all('td')]
        try:
            if tds[1] != '':
                chinese = tds[0]
                try:
                    value = int(tds[1])
                except:
                    value = float(tds[1])
                income_sheet_dict.update({
                    chinese:{
                        '英文名稱':'',
                        '科目代號':'',
                        'Value':value
                    }
                })
        except:
            print(tr)
            print(tds)
    return income_sheet_dict
            
def parse_cash_flow_sheet_web_html(tables):
    table = tables[3]
    cash_flow_dict = {'英文名稱(GAAP)':'Cash Flow Statement',
                      '英文名稱(IFRS)':'Statement of Cash Flows'}
    
    for tr in table.find_all('tr'):
        tds = [td.text.strip().replace(',', '') for td in tr.find_all('td')]
        try:
            if tds[1] != '':
                chinese = tds[0]
                try:
                    value = int(tds[1])
                except:
                    value = float(tds[1])
                cash_flow_dict.update({
                    chinese:{
                        '英文名稱':'',
                        '科目代號':'',
                        'Value':value
                    }
                })
        except:
            print(tr)
            print(tds)
    return cash_flow_dict
        

def read_data_from_file_before_2019(year=2013, season=1):
    crawl_balance_sheet_zip(year, season)
    zip_file = ZipFile(os.path.join(savePath, f'{year}Q{season}.zip'))
    files_in_zip = [f.filename for f in zip_file.filelist if '.xml' in f.filename]
    tickers = [f.split('-')[5] for f in files_in_zip]
    return tickers
    
def insert_db_first_time(db):
    cur_y = datetime.today().year
    for year in range(2013, cur_y+1):
        for quarter in range(1, 5):
            crawl_balance_sheet_zip(year, quarter)
            if year < 2019:
                datas = crawl_data_before_2019(year, quarter)
            else:
                datas = read_data_from_file(year, quarter)
            if datas:
                db.insert_many(datas)
            else:
                print(year, quarter, datas)
                
def get_updated_quater(db):
    last_y = db.distinct('Year')[-1]
    last_q = sorted([x['Quarter'] for x in list(db.find({'Year':{'$eq':last_y}}))])[-1]
    return [int(last_y), int(last_q)]
    
            
def update_db(db):
    last_y, last_q = get_updated_quater(db)
    td = datetime.today()
    cur_y = td.year
    
    # Haven't  fill all data for the updated year
    # Then Fill first
    if last_y <= cur_y:
        if last_q < 4:
            year = last_y
            for quarter in range(last_q+1, 5):
                crawl_balance_sheet_zip(year, quarter)
                if year < 2019:
                    datas = crawl_data_before_2019(year, quarter)
                else:
                    datas = read_data_from_file(year, quarter)
                if datas:
                    db.insert_many(datas)
                else:
                    print(year, quarter, datas)
        last_y += 1
    
    # Keep update Data               
    for year in range(last_y, cur_y):
        for quarter in range(1, 5):
            crawl_balance_sheet_zip(year, quarter)
            if year < 2019:
                datas = crawl_data_before_2019(year, quarter)
            else:
                datas = read_data_from_file(year, quarter)
            if datas:
                db.insert_many(datas)
            else:
                print(year, quarter, datas)
                    
   # update newest data
    publish_date_list = final_publish_date(cur_y)
    for i, publish_date in enumerate(publish_date_list):
        year, quarter = publish_date.year, i+1
        cnt = db.find({'Year':str(year), 'Quarter':str(quarter)}).count()
        if td > publish_date and not cnt:
            crawl_balance_sheet_zip(year, quarter)
            datas = read_data_from_file(year, quarter)
            if datas:
                db.insert_many(datas)
            else:
                print(year, quarter, datas)
            
if __name__ == '__main__':
    client = MongoClient('mongodb://kevin:j7629864@localhost:27017')
    
    schema = client['admin']
    dbs = schema.list_collection_names()
    db_name = 'TWSE.Fundmental'
    db = schema[db_name]
    first_create = db_name not in dbs
    first_create = db.count() == 0
    if first_create:
        db.create_index([('Ticker', 1), ('Year', 1), ('Quarter', 1)])
        insert_db_first_time(db)
    
    update_db(db)