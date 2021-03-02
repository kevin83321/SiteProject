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
    
def CassandraInsert(datas):
    session = Cassandra()
    batch=BatchStatement()
    # temp_data = [dict(exchange='TW', assets_type='Stock', symbol_code='2330', kline_period='1440', kline_datetime='2021/02/24', close_price='625.00', high_price='636.00', low_price='625.00', open_price='627.00', pkno=None, trans_volume='69675637', update_date='2021/02/24', update_prog_cd='MarketApi.FormMarketApi', update_time='15:12:17', update_user_id='Test')]
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
        batch.add(SimpleStatement(f"INSERT INTO MARKET103 ({cql_k}) VALUES ({cql_v})"), 
                    tuple(temp_v))
        temp_v = []
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