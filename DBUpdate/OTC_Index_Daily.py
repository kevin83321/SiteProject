# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
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

def crawlOTCIndex(date):
    sDate = "/".join([str(date.year-1911), date.strftime("%m/%d")])
    url = f'https://www.tpex.org.tw/web/stock/aftertrading/index_summary/summary_result.php?l=zh-tw&d={sDate}&_=1662691976535'
    data = crawl_json_data(url)

    output_data = []
    for d in data["aaData"]:
        output_data.append({
            "Date":date.strftime("%Y-%m-%d"),
            "IndexName":d[0].strip(),
            "Close":d[1]
        })
    return output_data

def main():
    try:
        start_time = time.time()
        client = Mongo()
        schema = client['admin']
        table_Interday_name = 'OTC.HistoricalPrice.Index.Interday'
        collections = schema.list_collection_names()
        Interday_db_not_found = table_Interday_name not in collections
        Interday_table = schema[table_Interday_name]
        if all([Interday_db_not_found]):
            Interday_table.create_index([('Date', 1), ('IndexName', 1)], unique=True)
            start_date = datetime(2016, 1, 4)
        else:
            Interday_cnt = Interday_table.count()
            if not all([Interday_cnt]):
                Interday_table.create_index([('Date', 1), ('IndexName', 1)], unique=True)
                start_date = datetime(2016, 1, 4)
            else:
                start_date = datetime.strptime(Interday_table.distinct('Date')[-1], '%Y-%m-%d') + timedelta(days=1)
        
        end_date = datetime.today()
        dates = date_range(start_date, end_date)
        for date in dates:
            try:
                print(f'crawl {date}')
                kBar = crawlOTCIndex(date)
            except Exception as e:
                print(f'{date} has no data')
                time.sleep(10)
                continue
            else:
                try:
                    Interday_table.insert_many(kBar)
                except:
                    pass
                time.sleep(5)
        duration = time.time() - start_time
    except Exception as e:
        Tele().sendMessage('Update Interday OTC Index Data Failed', group='UpdateMessage')
        print(e)
    else:
        Tele().sendMessage(f'Update Interday OTC Index Data Success, cost {round(duration, 2)} seconds.', group='UpdateMessage')

if __name__ == '__main__':
    # crawlOTCIndex(datetime(2022,9,8))
    main()