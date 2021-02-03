# -*- encoding: UTF-8 -*-
# CopyRight© : XIQICapital 希奇資本
# 爬取證交所有上市的ETF成分股
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.11.19
# Update: add log write into cmd
# Version: 1

__updated__ = '2021-01-31 21:38:15'
from datetime import datetime, timedelta
from pandas import date_range
import time
from modules import Mongo, Tele, crawl_json_data

def crawl5SecIndex(date):
    try:
        dateStr = date
        if isinstance(dateStr, datetime):
            dateStr = dateStr.strftime('%Y-%m-%d')
        url = f'https://www.twse.com.tw/exchangeReport/MI_5MINS_INDEX?response=json&date={dateStr.replace("-","")}'
        data = crawl_json_data(url)
        
        cols = data['fields']
        datas = data['data']
        KBar_dict = {}
        full_dict_list = []
        for d in datas:
            for col, idx in zip(cols[1:], d[1:]):
                datatime = d[0].strip()
                if len(datatime) == 5:
                    datatime += ':00'
                close = float(idx.replace(',',''))
                full_dict_list.append({
                    'Date':dateStr,
                    'Time':datatime,
                    "IndexName":col,
                    'Close':close
                })
                if col not in KBar_dict:
                    KBar_dict[col] = {
                        'Date':dateStr,
                        'IndexName':col,
                        'Open':close,
                        'High':close,
                        'Low':close,
                        'Close':close,
                    }
                else:
                    KBar_dict[col]['High'] = max(KBar_dict[col]['High'], close)
                    KBar_dict[col]['Low'] = min(KBar_dict[col]['Low'], close)
                    KBar_dict[col]['Close'] = close
    except ConnectionError:
        time.sleep(5)
        return crawl5SecIndex(dateStr)
    except Exception as e:
        raise e
    else:
        return full_dict_list, list(KBar_dict.values())

if __name__ == '__main__':
    try:
        start_time = time.time()
        client = Mongo()
        schema = client['admin']
        table_Intraday_name = 'TWSE.HistoricalPrice.Index.Intraday'
        table_Interday_name = 'TWSE.HistoricalPrice.Index.Interday'
        collections = schema.list_collection_names()
        Intraday_db_not_found = table_Intraday_name not in collections
        Interday_db_not_found = table_Interday_name not in collections
        Intraday_table = schema[table_Intraday_name]
        Interday_table = schema[table_Interday_name]
        if all([Intraday_db_not_found, Interday_db_not_found]):
            Intraday_table.create_index([('Date', 1), ('Time', 1), ('IndexName', 1)], unique=True)
            Interday_table.create_index([('Date', 1), ('IndexName', 1)], unique=True)
            start_date = datetime(2004, 10, 15)
        else:
            Intraday_cnt = Intraday_table.count()
            Interday_cnt = Interday_table.count()
            if not all([Interday_cnt, Intraday_cnt]):
                Intraday_table.create_index([('Date', 1), ('Time', 1), ('IndexName', 1)], unique=True)
                Interday_table.create_index([('Date', 1), ('IndexName', 1)], unique=True)
                start_date = datetime(2004, 10, 15)
            else:
                start_date = datetime.strptime(Interday_table.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
        
        end_date = datetime.today()
        dates = date_range(start_date, end_date)
        full_Kbar = []
        for date in dates:
            try:
                print(f'crawl {date}')
                full_dict, kBar = crawl5SecIndex(date)
            except Exception as e:
                print(f'{date} has no data')
                time.sleep(10)
                continue
            else:
                try:
                    Intraday_table.insert_many(full_dict)
                except:
                    pass
                try:
                    Interday_table.insert_many(kBar)
                except:
                    pass
                time.sleep(5)
        duration = time.time() - start_time
    except Exception as e:
        Tele().sendMessage('Update Intraday Index Data Failed', group='UpdateMessage')
        print(e)
    else:
        Tele().sendMessage(f'Update Intraday Index Data Success, cost {round(duration, 2)} seconds.', group='UpdateMessage')