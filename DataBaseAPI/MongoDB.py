# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.06.06
# Update: 2020.06.06
# Version: Test
# mongo

from pymongo import MongoClient
from Config import getConnectionConfig
from datetime import datetime

user, password, ip, port = getConnectionConfig()

class MongoDB:

    _connection = MongoClient(f'mongodb://{user}:{password}@{ip}:{port}')

    @staticmethod
    def reConnect(self, user, password, ip, port):
        self._connection = MongoClient(f'mongodb://{user}:{password}@{ip}:{port}')    

    def insert(self):
        pass

    @staticmethod
    def get(self, db_name, table_name, Ticker, startDate=None, endDate=None, limited=100):
        table = self._connection[db_name][table_name]
        if startDate is not None and endDate is not None:
            if isinstance(startDate, datetime): startDate = startDate.strftime("%Y-%m-%d")
            if isinstance(endDate, datetime): endDate = endDate.strftime("%Y-%m-%d")
            return list(table.find({'Ticker':{'$eq':Ticker}, 'Date':{'$gte':startDate, '$lte':endDate}}).limit(limited))
        elif startDate is not None:
            if isinstance(startDate, datetime): startDate = startDate.strftime("%Y-%m-%d")
            return table.find({'Ticker':{'$eq':Ticker}, 'Date':{'$gte':startDate}}).limit(limited)
        elif endDate is not None:
            if isinstance(endDate, datetime): endDate = endDate.strftime("%Y-%m-%d")
            return table.find({'Ticker':{'$eq':Ticker}, 'Date':{'$lte':endDate}}).limit(limited)
