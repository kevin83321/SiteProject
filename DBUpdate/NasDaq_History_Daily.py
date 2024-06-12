# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
# 爬取所有美股的股票交易日資料
# Author: Kevin Cheng 鄭圳宏
# Create: 2024.06.12
# Update: add log write into cmd
# Version: 1

__updated__ = '2022-09-12 09:30:57'

from pandas import DataFrame, date_range, read_csv
from datetime import timedelta, datetime
import os
import time
import re
from modules import Tele, Mongo, requests
from Log import TransforException

def crawl_nasdaq_stock_daily(symbol:str="MSFT", dt:datetime=datetime.today(), first_time:bool=True):
    start_date = dt - timedelta(1)
    if first_time:
        start_date -= timedelta(31*120)
    url = f"https://api.nasdaq.com/api/quote/{symbol}/historical?assetclass=stocks&fromdate={start_date.strftime('%Y-%m-%d')}&todate={dt.strftime('%Y-%m-%d')}&limit=9999"

    headers = {
        "authority":"api.nasdaq.com",
        "method":"GET",
        # "path":"/api/quote/AAPL/historical?assetclass=stocks&fromdate=2014-06-12&limit=9999&todate=2024-06-12&random=35",
        "scheme":"https",
        "Accept":"application/json, text/plain, */*",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin":"https://www.nasdaq.com",
        "Priority":"u=1, i",
        "Referer":"https://www.nasdaq.com/",
        "Sec-Ch-Ua":'"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile":"?0",
        "Sec-Ch-Ua-Platform":'"Windows"',
        "Sec-Fetch-Dest":"empty",
        "Sec-Fetch-Mode":"cors",
        "Sec-Fetch-Site":"same-site",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    res = requests.get(url, headers=headers)
    json = res.json()
    df = DataFrame(json["data"]["tradesTable"]["rows"])
    df.columns = [x.capitalize() for x in df.columns]
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.replace("$", "").replace("/", "-").replace(",", ""))
    print(df.head(5))

if __name__ == "__main__":
    crawl_nasdaq_stock_daily()