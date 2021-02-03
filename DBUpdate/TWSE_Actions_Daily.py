# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的股票的除權、息，分割，合併
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Version: 1

__updated__ = '2021-01-31 12:06:48'

from pandas import DataFrame, concat, date_range
from bs4 import BeautifulSoup as bs
import re, time, json, urllib.request, os
from datetime import timedelta, datetime
from modules import Tele, Mongo, crawl_json_data
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): 
    path = os.getcwd()
actionpath = os.path.join(path, 'TWSE_Actions')
if not os.path.isdir(actionpath): 
    os.makedirs(actionpath)

def TSE_ExRightDividend(start, end):

    selectdate_start = start.strftime('%Y%m%d')
    selectdate_end = end.strftime('%Y%m%d')

    url = f'https://www.twse.com.tw/exchangeReport/TWT49U?response=json&strDate={selectdate_start}&endDate={selectdate_end}'
    js = crawl_json_data(url)
    url1 = 'https://www.twse.com.tw'
    output = DataFrame(columns = ['Date', 'Ticker', 'Action', 'Value'])
    try:
        js['data']
        k = 0
        for i in range(len(js['data'])):
            ticker = js['data'][i][1]

            res = urllib.request.Request(url1 + js['data'][i][11].split('\'')[1].split('.')[6]) 
            res.add_header('upgrade-insecure-requests', '1')
            res.add_header('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
            rd = urllib.request.urlopen(res).read().decode()
            soup = bs(rd, "html.parser")
            RawData1 = DataFrame(columns = ['ExRightDividend'])
            j = 0
            for tr in soup.select('table tr')[0:5]:
                for td in tr.select('td')[1:]:
                    RawData1.loc[j, 'ExRightDividend'] = re.sub('[^0-9.]', '', str(td.text))    
                    j = j + 1        
            if len(RawData1) > 0:          
               if float(RawData1.iat[4,0]) != 0 and float(RawData1.iat[2,0]) != 0: #Ex Right(XR) & Ex Dividend(XD)
                  # Ex Dividend(XD) 除息
                  output.loc[k, 'Date'] = datetime.strptime(js['data'][i][11].split('\'')[1][-8:], '%Y%m%d').date().strftime("%Y-%m-%d")
                  output.loc[k, 'Ticker'] = ticker
                  output.loc[k, 'Action'] = 'XD'  
                  output.loc[k, 'Value'] = RawData1.iat[2,0]
                  #Ex Right(XR) 除權
                  output.loc[k + 1, 'Date'] = datetime.strptime(js['data'][i][11].split('\'')[1][-8:], '%Y%m%d').date().strftime("%Y-%m-%d")
                  output.loc[k + 1, 'Ticker'] = ticker
                  output.loc[k + 1, 'Action'] = 'XR'  
                  output.loc[k + 1, 'Value'] = RawData1.iat[4,0]
                  k = k + 2
               elif float(RawData1.iat[2,0]) != 0: # Ex Dividend(XD) 除息
                  output.loc[k, 'Date'] = datetime.strptime(js['data'][i][11].split('\'')[1][-8:], '%Y%m%d').date().strftime("%Y-%m-%d")          
                  output.loc[k, 'Ticker'] = ticker
                  output.loc[k, 'Action'] = 'XD'  
                  output.loc[k, 'Value'] = RawData1.iat[2,0]
                  k = k + 1
               elif float(RawData1.iat[4,0]) != 0: #Ex Right(XR) 除權
                  output.loc[k, 'Date'] = datetime.strptime(js['data'][i][11].split('\'')[1][-8:], '%Y%m%d').date().strftime("%Y-%m-%d")          
                  output.loc[k, 'Ticker'] = ticker
                  output.loc[k, 'Action'] = 'XR'  
                  output.loc[k, 'Value'] = RawData1.iat[4,0]
                  k = k + 1 
            time.sleep(5) 
    except:
        pass 
      
    return output


def TSE_CapitalReduction(start, end):

    selectdate_start = start.strftime('%Y%m%d')
    selectdate_end = end.strftime('%Y%m%d')
    
    url = f'https://www.twse.com.tw/exchangeReport/TWTAUU?response=json&strDate={selectdate_start}&endDate={selectdate_end}'
    js = crawl_json_data(url)
    output = DataFrame(columns = ['Date', 'Ticker', 'Action', 'Value'])      
    try:
        js['data']
        k = 0
        url1 = 'https://www.twse.com.tw/zh'
        for i in range(len(js['data'])):
            """
            res1 = requests.get(url1 + js['data'][i][10].split('\'')[1].split('.')[6], timeout = 5)
            soup1 = bs(res1.text, "html.parser") 
            """
            res1 = urllib.request.Request(url1 + js['data'][i][10].split('\'')[1].split('.')[6])
            res1.add_header('upgrade-insecure-requests', '1')
            res1.add_header('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
            rd1 = urllib.request.urlopen(res1).read().decode()
            soup1 = bs(rd1, "html.parser") 
            j = 0
            RawData1 = DataFrame(columns=['CapitalReduction'])
            for tr1 in soup1.select('table tr')[2:5]:
                for td1 in tr1.select('td')[1:]:
                    RawData1.loc[j, 'CapitalReduction'] = re.sub('[^0-9.]', '', str(td1.text))
                    j = j + 1
            if float(RawData1.loc[2,'CapitalReduction']) == 0:
               output.loc[k, 'Date'] = '-'.join([str(int(js['data'][i][0].split('/')[0]) + 1911), js['data'][i][0].split('/')[1], js['data'][i][0].split('/')[2]])
               output.loc[k, 'Ticker'] = js['data'][i][1]
               output.loc[k, 'Action'] = 'RS' #換發新股 Replacement issue of stock 
               output.loc[k, 'Value'] = RawData1.loc[1,'CapitalReduction']
               k = k + 1
            else:
               output.loc[k, 'Date'] = '-'.join([str(int(js['data'][i][0].split('/')[0]) + 1911), js['data'][i][0].split('/')[1], js['data'][i][0].split('/')[2]])
               output.loc[k, 'Ticker'] = js['data'][i][1]
               output.loc[k, 'Action'] = 'RS' #換發新股 Replacement issue of stock 
               output.loc[k, 'Value'] = RawData1.loc[1,'CapitalReduction']
               output.loc[k + 1, 'Date'] = '-'.join([str(int(js['data'][i][0].split('/')[0]) + 1911), js['data'][i][0].split('/')[1], js['data'][i][0].split('/')[2]])
               output.loc[k + 1, 'Ticker'] = js['data'][i][1]
               output.loc[k + 1, 'Action'] = 'RC' #配發現金 Return of capital
               output.loc[k + 1, 'Value'] = RawData1.loc[2,'CapitalReduction']
               k = k + 2  
            time.sleep(5)  
    except:
        pass 
 
    return output


def OTC_ExRightDividend(start, end):
    
    selectdate_start = start.strftime('%Y/%m/%d')
    selectdate_end = end.strftime('%Y/%m/%d')

    urlfirst = 'https://www.tpex.org.tw/web/stock/exright/dailyquo/exDailyQ_result.php?l=en-us&d=' 
    urllast = '&ed='
    url = urlfirst + selectdate_start + urllast + selectdate_end
    js = crawl_json_data(url)
    output = DataFrame(columns = ['Date', 'Ticker', 'Action', 'Value']) 
    try:
        data = js['aaData'] 
        k = 0
        for i in range(len(data)):
            if data[i][7] == 'DR':
                output.loc[k, 'Date'] = data[i][0].replace('/', '-')
                output.loc[k, 'Ticker'] = data[i][1]
                output.loc[k, 'Action'] = 'XR'
                output.loc[k, 'Value'] = float(data[i][13])
                output.loc[k + 1, 'Date'] = data[i][0].replace('/', '-')
                output.loc[k + 1, 'Ticker'] = data[i][1]
                output.loc[k + 1, 'Action'] = 'XD'
                output.loc[k + 1, 'Value'] = float(data[i][12])       
                k = k + 2
            elif data[i][7] == 'XD':
                output.loc[k, 'Date'] = data[i][0].replace('/', '-')
                output.loc[k, 'Ticker'] = data[i][1]
                output.loc[k, 'Action'] = 'XD'
                output.loc[k, 'Value'] = float(data[i][12])
                k = k + 1
            elif data[i][7] == 'XR':
                output.loc[k, 'Date'] = data[i][0].replace('/', '-')
                output.loc[k, 'Ticker'] = data[i][1]
                output.loc[k, 'Action'] = 'XR'
                output.loc[k, 'Value'] = float(data[i][13])
                k = k + 1
        output = output[output['Value'] > 0]   #OTC 除權資料包括“增資”，但是增資卻不會影響股價 ex: 2017/04/20 
    except:
        pass
    
    return output


def OTC_CapitalReduction(start, end):
    
    selectdate_start = start.strftime('%Y/%m/%d')
    selectdate_end = end.strftime('%Y/%m/%d')

    urlfirst = 'https://www.tpex.org.tw/web/stock/exright/revivt/revivt_result.php?l=en-us&d=' 
    urllast = '&ed='
    url = urlfirst + selectdate_start + urllast + selectdate_end
    js = crawl_json_data(url)
    output = DataFrame(columns = ['Date', 'Ticker', 'Action', 'Value']) 
    try:
        data = js['aaData'] 
        k = 0      
        for i in range(len(data)):
            if data[i][8] == 'Making up losses': #彌補虧損 
                output.loc[k, 'Date'] = '-'.join([str(data[i][0])[0:4], str(data[i][0])[4:6], str(data[i][0])[6:8]])
                output.loc[k, 'Ticker'] = data[i][1]
                output.loc[k, 'Action'] = 'RS'
                output.loc[k, 'Value'] = float(re.search('parm6=(.*)&amp;parm7', data[i][9])[1])
                k = k + 1
            elif data[i][8] == 'Cash refund': #現金減資
                output.loc[k, 'Date'] = '-'.join([str(data[i][0])[0:4], str(data[i][0])[4:6], str(data[i][0])[6:8]])
                output.loc[k, 'Ticker'] = data[i][1]
                output.loc[k, 'Action'] = 'RS'
                output.loc[k, 'Value'] = float(re.search('parm6=(.*)&amp;parm7', data[i][9])[1])
                output.loc[k + 1, 'Date'] = '-'.join([str(data[i][0])[0:4], str(data[i][0])[4:6], str(data[i][0])[6:8]])
                output.loc[k + 1, 'Ticker'] = data[i][1]
                output.loc[k + 1, 'Action'] = 'RC'
                output.loc[k + 1, 'Value'] = float(re.search('parm7=(.*)&amp;parm8', data[i][9])[1])
                k = k + 2 
    except:
        pass
    
    return output

def Main_Crawler(date):
    try:
        Importdata = DataFrame()
        ###   TSE_ExRightDividend   ###
        output = TSE_ExRightDividend(date, date)
        Importdata = concat([Importdata, output])

        ####   TSE_CapitalReduction   ###
        output = TSE_CapitalReduction(date, date)
        Importdata = concat([Importdata, output]) 


        ####   OTC_ExRightDividend   ###
        output = OTC_ExRightDividend(date, date)
        Importdata = concat([Importdata, output])        
        
        ####   OTC_CapitalReduction   ###
        output = OTC_CapitalReduction(date, date)
        Importdata = concat([Importdata, output])

        Importdata.columns = ['Date', 'Ticker', 'Action', 'Value']
    except:
        return
    else:
        return Importdata
        
if __name__ == "__main__":
    client = Mongo()
    table = client['admin']['TWSE']['Actions']
    start_date = datetime.strptime(table.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
    date_range = date_range(start_date, datetime.today())
    
    for date in date_range:###   Date   ###
        
        Importdata = Main_Crawler(date)
        
        if Importdata is not None:
            if not Importdata.empty:
                Importdata.to_csv(os.path.join(actionpath, f'Daily_{date.strftime("%Y-%m-%d")}.txt'), sep = '\t', index = None)
                data = [dict(x._asdict().items()) for x in Importdata.itertuples()]
                for x in data: del x['Index']
                table.insert_many(data)
        time.sleep(5)

    # send finish message
    Tele().sendMessage('Update TWSE Actions success', group='UpdateMessage')