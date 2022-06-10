# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
# 爬取所有上市上櫃的三大法人
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Update: add log write into cmd
# Version: 1

__updated__ = '2022-02-26 17:29:39'

from pandas import DataFrame, date_range, read_csv
from datetime import timedelta, datetime
import os
import time
import re
from modules import Tele, Mongo, crawl_json_data

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

## =========================
## 共用Function
## =========================
def update_data_dict(d):
    if 'Index' in d:
        del d['Index']
    delete_k = []
    for key in d.keys():
        if re.match(r'_[0-9]*', key):
            delete_k.append(key)
    for key in delete_k:
        d.pop(key)
    # d['Adj Close'] = d['Close']
    return d

def ParseData(x, key=""):
    try:
        if key in ["Ticker", "Name", "Date"]:
            return x.strip()
        x = x.strip().replace(',', '')
        if x.isnumeric():
            return int(x)
        elif "-" in x:
            return int(x)
        return float(x)
    except:
        return x

col_map = {
        "證券代號":"Ticker",
        "證券名稱":"Name",
        "買進股數":"Buy",
        "賣出股數":"Sell",
        "買賣超股數":"OverBS",
    }

col_otc = ['Ticker', "Name", "Buy", "Sell", "OverBS","Date"]

## =========================
## TWSE (上市)
## =========================
def GetData_SITC(dt=datetime(2004,12,17)):
    """
    TWSE
    Security Investment Trust Companies - SITC (投信)
    Start With 2004-12-17
    """
    try:
        dtStr = dt.strftime("%Y-%m-%d")
        url = f"https://www.twse.com.tw/fund/TWT44U?response=json&date={dtStr.replace('-', '')}&_=1645862099918"
        js = crawl_json_data(url)

        cols = js['fields'][1:]
        raw_datas = js['data']
        final_datas = []
        for data in raw_datas:
            d = dict((col_map[k], ParseData(v, col_map[k])) for k, v in zip(cols, data[1:]))
            d.update({"Date":dtStr})
            final_datas.append(d)
    except:
        print(f"Dealer TWSE Error : {e}")
    else:
        return final_datas

def GetData_Dealer(dt=datetime(2004,12,17)):
    """
    TWSE
    Dealer (自營商)
    Start With 2004-12-17
    """
    dtStr = dt.strftime("%Y-%m-%d")
    url = f"https://www.twse.com.tw/fund/TWT43U?response=json&date={dtStr.replace('-', '')}&_=1645862095882"
    js = crawl_json_data(url)

    cols = js['fields'][:2] + js['fields'][-3:]
    raw_datas = js['data']
    final_datas = []
    for data in raw_datas:
        try:
            d = dict((col_map[k], ParseData(v, col_map[k])) for k, v in zip(cols, data[:2]+data[-3:]))
            d.update({"Date":dtStr})
            final_datas.append(d)
        except:
            print(data[:2]+data[-3:])
            break
    return final_datas

def GetData_Foreign(dt=datetime(2004,12,17)):
    """
    TWSE
    Foreign Investors include Mainland Area Investors (外資含陸資)
    Start With 2004-12-17
    """
    dtStr = dt.strftime("%Y-%m-%d")
    url = f"https://www.twse.com.tw/fund/TWT38U?response=json&date={dtStr.replace('-', '')}&_=1645862108043"
    js = crawl_json_data(url)

    cols = js['fields'][1:3] + js['fields'][-3:]
    raw_datas = js['data']
    final_datas = []
    for data in raw_datas:
        try:
            d = dict((col_map[k], ParseData(v, col_map[k])) for k, v in zip(cols, data[1:3]+data[-3:]))
            d.update({"Date":dtStr})
            final_datas.append(d)
        except:
            print(data[:2]+data[-3:])
            break
    return final_datas

## =========================
## OTC (上櫃)
## =========================
def GetData_SITC_OTC(dt=datetime(2007,4,23)):
    """
    OTC
    Security Investment Trust Companies - SITC (投信)
    Start With 2007-04-23
    """
    dtStr = dt.strftime("%Y-%m-%d")
    dateStr = f"{str(dt.year - 1911)}{dt.strftime('/%m/%d')}"
    sellUrl = f"https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=sell&d={dateStr}&_=1645871498835"
    buyUrl = f"https://www.tpex.org.tw/web/stock/3insti/sitc_trading/sitctr_result.php?l=zh-tw&t=D&type=buy&d={dateStr}&_=1645871498835"
    js_sell = crawl_json_data(sellUrl)
    js_buy = crawl_json_data(buyUrl)
    final_datas = []
    raw_datas = js_sell['aaData'] + js_buy['aaData']
    for data in raw_datas:
        rows = data[1:] + [dtStr]
        final_datas.append(dict((k, ParseData(v, col_map[k])) for k, v in zip(col_otc, rows)))
    return final_datas

def GetData_Dealer_OTC(dt=datetime(2007,4,23)):
    """
    OTC
    Dealer (自營商)
    Start With 2007-04-23
    """
    dtStr = dt.strftime("%Y-%m-%d")
    dateStr = f"{str(dt.year - 1911)}{dt.strftime('/%m/%d')}"
    final_datas = []
    if dt >= datetime(2014,12,1):
        sellUrl = f"https://www.tpex.org.tw/web/stock/3insti/dealer_trading/dealtr_hedge_result.php?l=zh-tw&t=D&type=sell&d={dateStr}&_=1645869758482"
        buyUrl = f"https://www.tpex.org.tw/web/stock/3insti/dealer_trading/dealtr_hedge_result.php?l=zh-tw&t=D&type=buy&d={dateStr}&_=1645869758482"
    else:
        sellUrl = f"https://www.tpex.org.tw/web/stock/3insti/dealer_trading/dealtr_result.php?l=zh-tw&t=D&type=sell&d={dateStr}&_=1645870460266"
        buyUrl = f"https://www.tpex.org.tw/web/stock/3insti/dealer_trading/dealtr_result.php?l=zh-tw&t=D&type=buy&d={dateStr}&_=1645870460266"
    js_sell = crawl_json_data(sellUrl)
    js_buy = crawl_json_data(buyUrl)
    raw_datas = js_sell['aaData'] + js_buy['aaData']
    for data in raw_datas:
        if dt >= datetime(2014,12,1):
            rows = [data[1],data[2],data[3]+data[6],data[4]+data[7],data[-1],dtStr]
        else:
            rows = data[1:] + [dtStr]
        final_datas.append(dict((k, ParseData(v, col_map[k])) for k, v in zip(col_otc, rows)))
    return final_datas

def GetData_Foreign_OTC(dt=datetime(2007,4,23)):
    """
    OTC
    Foreign Investors include Mainland Area Investors (外資含陸資)
    Start With 2007-04-23
    """
    dtStr = dt.strftime("%Y-%m-%d")
    dateStr = f"{str(dt.year - 1911)}{dt.strftime('/%m/%d')}"
    
    sellUrl = f"https://www.tpex.org.tw/web/stock/3insti/qfii_trading/forgtr_result.php?l=zh-tw&t=D&type=sell&d={dateStr}&_=1645871930051"
    buyUrl = f"https://www.tpex.org.tw/web/stock/3insti/qfii_trading/forgtr_result.php?l=zh-tw&t=D&type=buy&d={dateStr}&_=1645871930051"
    js_sell = crawl_json_data(sellUrl)
    js_buy = crawl_json_data(buyUrl)
    final_datas = []
    raw_datas = ''
    raw_datas = js_sell['aaData'] + js_buy['aaData']
    for data in raw_datas:
        rows = data[1:3] + data[-3:] + [dtStr]
        for i in range(-4,-1):
            rows[i] = int(ParseData(rows[i]) * 1000)
        final_datas.append(dict((k, ParseData(v, col_map[k])) for k, v in zip(col_otc, rows)))
    return final_datas

def GetStartDate(client, start_date=datetime(2004,12,17)):
    schema = client['admin']
    db_SITC = 'TWSE.ForeignAndOther.SITC'
    db_Dealer = 'TWSE.ForeignAndOther.Dealer'
    db_Foreign = 'TWSE.ForeignAndOther.Foreign'
    collections = schema.list_collection_names()
    
    SITC_db_not_found = db_SITC not in collections
    Dealer_db_not_found = db_Dealer not in collections
    Foreign_db_not_found = db_Foreign not in collections
    tableSITC = client['admin'][db_SITC]
    tableDealer = client['admin'][db_Dealer]
    tableForeign = client['admin'][db_Foreign]
    
    start_Foreign = start_Dealer = start_SITC = start_date
    if all([SITC_db_not_found, Dealer_db_not_found, Foreign_db_not_found]):
        tableSITC.create_index([('Date', 1), ('Ticker', 1)], unique=True)
        tableDealer.create_index([('Date', 1), ('Ticker', 1)], unique=True)
        tableForeign.create_index([('Date', 1), ('Ticker', 1)], unique=True)
    else:
        tableSITC_cnt = tableSITC.count()
        tableDealer_cnt = tableDealer.count()
        tableForeign_cnt = tableForeign.count()
        if not all([tableSITC_cnt, tableDealer_cnt, tableForeign_cnt]):
            tableSITC.create_index([('Date', 1), ('Ticker', 1)], unique=True)
            tableDealer.create_index([('Date', 1), ('Ticker', 1)], unique=True)
            tableForeign.create_index([('Date', 1), ('Ticker', 1)], unique=True)
        else:
            start_SITC = datetime.strptime(tableSITC.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
            start_Dealer = datetime.strptime(tableDealer.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
            start_Foreign = datetime.strptime(tableForeign.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
            start_date = min(start_SITC, start_Dealer, start_Foreign)
    return ((start_SITC, start_Dealer, start_Foreign), (tableSITC, tableDealer, tableForeign))

def DoSITC(data_path, table, date, start, exchange = "TWSE"):
    try:
        data = []
        if date >= start:
            if os.path.isfile(os.path.join(
                    data_path, f"{date.strftime('%Y-%m-%d')}.txt")):# and False:
                try:
                    df = read_csv(os.path.join(
                        data_path, f"{date.strftime('%Y-%m-%d')}_SITC.txt"), sep='\t')
                    data = [update_data_dict(x) for x in list(df.T.to_dict().values())]
                except:
                    if exchange == "TWSE":
                        data = GetData_SITC(date)
                    else:
                        data = GetData_SITC_OTC(date)
            else:
                if exchange == "TWSE":
                    data = GetData_SITC(date)
                else:
                    data = GetData_SITC_OTC(date)
        if len(data) > 0:
            DataFrame(data).to_csv(os.path.join(
                data_path, f"{date.strftime('%Y-%m-%d')}_SITC.txt"), sep='\t', index=None, float_format='%g')
            table.insert_many(data)
    except Exception as e:
        print(f"SITC Error : {e}")

def DoDealer(data_path, table, date, start, exchange = "TWSE"):
    try:
        data = []
        if date >= start:
            if os.path.isfile(os.path.join(
                    data_path, f"{date.strftime('%Y-%m-%d')}.txt")):# and False:
                try:
                    df = read_csv(os.path.join(
                        data_path, f"{date.strftime('%Y-%m-%d')}_Dealer.txt"), sep='\t')
                    data = [update_data_dict(x) for x in list(df.T.to_dict().values())]
                except:
                    if exchange == "TWSE":
                        data = GetData_Dealer(date)
                    else:
                        data = GetData_Dealer_OTC(date)
            else:
                if exchange == "TWSE":
                    data = GetData_Dealer(date)
                else:
                    data = GetData_Dealer_OTC(date)
        if len(data) > 0:
            DataFrame(data).to_csv(os.path.join(
                data_path, f"{date.strftime('%Y-%m-%d')}_Dealer.txt"), sep='\t', index=None, float_format='%g')
            table.insert_many(data)
    except Exception as e:
        print(f"Dealer Error : {e}")

def DoForeign(data_path, table, date, start, exchange = "TWSE"):
    try:
        data = []
        if date >= start:
            if os.path.isfile(os.path.join(
                    data_path, f"{date.strftime('%Y-%m-%d')}.txt")):# and False:
                try:
                    df = read_csv(os.path.join(
                        data_path, f"{date.strftime('%Y-%m-%d')}_Foreign.txt"), sep='\t')
                    data = [update_data_dict(x) for x in list(df.T.to_dict().values())]
                except:
                    if exchange == 'TWSE':
                        data = GetData_Foreign(date)
                    else:
                        data = GetData_Foreign_OTC(date)
            else:
                if exchange == 'TWSE':
                    data = GetData_Foreign(date)
                else:
                    data = GetData_Foreign_OTC(date)
        # print(date, len(data))
        if len(data) > 0:
            DataFrame(data).to_csv(os.path.join(
                data_path, f"{date.strftime('%Y-%m-%d')}_Foreign.txt"), sep='\t', index=None, float_format='%g')
            table.insert_many(data)
    except Exception as e:
        print(f"Foreign Error : {e}")

def main():
    pass

if __name__ == "__main__":
    try:
        client = Mongo()
        start_dates, tables = GetStartDate(client)
        start_SITC, start_Dealer, start_Foreign = start_dates
        tableSITC, tableDealer, tableForeign = tables
        start_date = min(start_dates)
        # start_SITC = start_Dealer = start_Foreign = start_date = datetime(2005,3,3)
        dates = date_range(start_date, datetime.today())
        for date in dates:
            print(date)
            try:
                # crawl tse daily data
                try:
                    DoSITC(tsepath, tableSITC, date, start_SITC, exchange = "TWSE")
                    DoDealer(tsepath, tableDealer, date, start_Dealer, exchange = "TWSE")
                    DoForeign(tsepath, tableForeign, date, start_Foreign, exchange = "TWSE")
                except Exception as e:
                    print('TSE Foreign and others',e)
                try:
                    DoSITC(otcpath, tableSITC, date, start_SITC, exchange = "OTC")
                    DoDealer(otcpath, tableDealer, date, start_Dealer, exchange = "OTC")
                    DoForeign(otcpath, tableForeign, date, start_Foreign, exchange = "OTC")
                except Exception as e:
                    print('OTC Foreign and others',e)
                print(f'Update {date} Foreign and others success')
            except Exception as e:
                print('Foreign and others',e)
                
            time.sleep(10)

        # send finish message
        Tele().sendMessage('更新三大法人完成', group='UpdateMessage')
    except Exception as e:
        print("Main Loop Error : ",e)