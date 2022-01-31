# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取所有上市上櫃的股票交易日資料
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.07.01
# Update: add log write into cmd
# Version: 1

__updated__ = '2021-02-28 23:09:42'

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


def TSE_HistoricalPrice(i):
    output = []
    try:
        date = i.strftime('%Y%m%d')
        url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=' + \
            date + '&type=ALLBUT0999&_=1553846233285'

        js = crawl_json_data(url)
        data = js['data9']
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
            }))
    except Exception as e:
        print(e)
        pass
    return output


if __name__ == "__main__":
    try:
        client = Mongo()
        table = client['admin']['TWSE']['historicalPrice']
        start_date = datetime.strptime(sorted(table.distinct(
            'Date'))[-1], '%Y-%m-%d') + timedelta(days=1)
        # start_date = datetime(2022,1,5)
        # date_range = date_range(start_date, start_date)
        date_range = date_range(start_date, datetime.today())
        for date in date_range:
            print(date)
            try:
                # crawl tse daily data
                if os.path.isfile(os.path.join(
                        tsepath, f"{date.strftime('%Y-%m-%d')}.txt")):
                    try:
                        df_tse = read_csv(os.path.join(
                            tsepath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t')
                        data_tse = [update_data_dict(x) for x in list(df_tse.T.to_dict().values())]
                    except:
                        data_tse = TSE_HistoricalPrice(date)
                else:
                    data_tse = TSE_HistoricalPrice(date)
                if len(data_tse) > 0:
                    DataFrame(data_tse).to_csv(os.path.join(
                        tsepath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t', index=None, float_format='%g')
                    table.insert_many(data_tse)
                print(f'Update {date} Historical Price of tse success')
            except Exception as e:
                print('tse',e)
            try:
                # crawl otc daily data
                if os.path.isfile(os.path.join(
                        otcpath, f"{date.strftime('%Y-%m-%d')}.txt")):
                    try:
                        df_otc = read_csv(os.path.join(
                            otcpath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t')
                        data_otc = [update_data_dict(x) for x in list(df_otc.T.to_dict().values())]
                    except:
                        data_otc = OTC_HistoricalPrice(date)
                else:
                    data_otc = OTC_HistoricalPrice(date)
                if len(data_otc) > 0:
                    DataFrame(data_otc).to_csv(os.path.join(
                        otcpath, f"{date.strftime('%Y-%m-%d')}.txt"), sep='\t', index=None, float_format='%g')
                    table.insert_many(data_otc)
                print(f'Update {date} Historical Price of otc success')
            except Exception as e:
                print('otc',e)
            time.sleep(5)

        # send finish message
        # Line().sendMessage('Update Stock Historical Price success')
        Tele().sendMessage('Update Stock Historical Price success', group='UpdateMessage')
    except Exception as e:
        print("Main Loop Error : ",e)
