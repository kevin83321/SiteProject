# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.06.06
# Version: Test
# mongo

__updated__ = '2021-10-17 16:40:32'

from pymongo import MongoClient
from Config import getConnectionConfig
from datetime import datetime

user, password, ip, port = getConnectionConfig()

class MongoDB:

    _connection = MongoClient(f'mongodb://{user}:{password}@{ip}:{port}')

    @staticmethod
    def reConnect(user, password, ip, port):
        MongoDB._connection = MongoClient(f'mongodb://{user}:{password}@{ip}:{port}')

    @staticmethod
    def get(db_name, table_name, Ticker:str, StartDate=None, EndDate=None): #, limited=100
        table = MongoDB._connection['admin'][db_name][table_name]
        if not Ticker or not len(Ticker): return f'Ticker : {Ticker}, StartDate : {StartDate}, EndDate : {EndDate}'
        if StartDate is not None and EndDate is not None:
            if isinstance(StartDate, datetime): StartDate = StartDate.strftime("%Y-%m-%d")
            if isinstance(EndDate, datetime): EndDate = EndDate.strftime("%Y-%m-%d")
            return list(table.find({'Ticker':{'$in':Ticker.split(',')}, 'Date':{'$gte':StartDate, '$lte':EndDate}})) # .limit(limited))
        if StartDate is not None:
            if isinstance(StartDate, datetime): StartDate = StartDate.strftime("%Y-%m-%d")
            return list(table.find({'Ticker':{'$in':Ticker.split(',')}, 'Date':{'$gte':StartDate}})) # .limit(limited)
        if EndDate is not None:
            if isinstance(EndDate, datetime): EndDate = EndDate.strftime("%Y-%m-%d")
            return list(table.find({'Ticker':{'$in':Ticker.split(',')}, 'Date':{'$lte':EndDate}})) # .limit(limited)
        return f'Ticker : {Ticker}, StartDate : {StartDate}, EndDate : {EndDate}'

    @staticmethod
    def getAction(db_name, Ticker, StartDate, EndDate):
        table = MongoDB._connection['admin'][db_name]['Action']

