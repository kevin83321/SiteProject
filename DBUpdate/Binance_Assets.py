# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
# 爬取所有美股的股票/ETF 除權息歷史資料
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

import requests
import json

if __name__ == "__main__":
    url = "https://api.binance.com/api/v3/exchangeInfo"

    payload = {}
    headers = {
    'Content-Type': 'application/json'
    }

    res = requests.get(url, headers=headers, data=payload)
    json = res.json()

    datas = [x for x in json["symbols"] if x["quoteAsset"] == "USDT"]
    # df = DataFrame()
    # print(df.head(5))
    print(datas[0])
