# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.28
# Update: Create
# Version: 1

from PyDBFunc import Cassandra
from cassandra.query import SimpleStatement, BatchStatement

def CassandraRead():
    session = Cassandra()
    datas = session.execute("SELECT * FROM MARKET103 WHERE symbol_code='2330' AND kline_period='1440' AND update_user_id='Test' ALLOW FILTERING").all()
    
def CassandraInsert(database='MARKET103', datas=[]):
    session = Cassandra()
    batch = BatchStatement()
    i = 0
    for data in datas:
        temp_k = []
        temp_v = []
        if not temp_k:
            for k, v in data.items():
                temp_k.append(k)
                temp_v.append(v)
        else:
            for k in temp_k:
                temp_v.append(data[k])
        cql_k = ', '.join(temp_k)
        cql_v = ', '.join(['%s',]*len(temp_k))
        batch.add(SimpleStatement(f"INSERT INTO {database} ({cql_k}) VALUES ({cql_v})"), 
                    tuple(temp_v))
        temp_v = []
        i += 1
        if i >= 65535:
            session.execute(batch)
            batch = BatchStatement()
            i = 0
    session.execute(batch)
    
def CassandraDelete(table: str= 'MARKET103', exchange: str= 'TW',
                    assets_type: str= 'Stock', symbol_code: str='',
                    kline_period: str= '1440', kline_datetime: str='2021/02/24',
                    expand_condition: str= None):
    session = Cassandra()
    cql = f"DELETE FROM {table} WHERE exchange={exchange} AND assets_type={assets_type} AND symbol_code={symbol_code} AND kline_period={kline_period} AND kline_datetime={kline_datetime}"
    if expand_condition:
        cql += f' AND {expand_condition}'
    print(cql)
    session.execute(cql)