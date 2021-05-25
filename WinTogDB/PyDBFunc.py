# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.28
# Update: Create
# Version: 1

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from pymongo import MongoClient

import pyodbc

import configparser
import os
parent = os.path.dirname(os.path.abspath(__file__))

parser = configparser.ConfigParser()
parser.read(os.path.join(parent, 'database.conf'))
parser.sections()

def Mongo():
    config = parser['MONGOSETTING']
    user = config['user']
    password = config['password']
    ip = config['ip']
    port = config['port']
    client = MongoClient(f"mongodb://{user}:{password}@{ip}:{port}")
    return client['admin']

def Cassandra(db='casmarket'):
    config = parser['CASSANDRASETTING']
    user = config['user']
    password = config['password']
    ip = config['ip']
    port = config['port']
    
    auth_provider = PlainTextAuthProvider(username=user, password=password)
    cluster = Cluster([ip], port=int(port), auth_provider=auth_provider)
    return cluster.connect(db)

def SQLServer():
    config = parser['SQLSERVERSETTING']
    user = config['user']
    password = config['password']
    ip = config['ip']
    db = config['db']
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'+f'SERVER={ip};DATABASE={db};UID={user};PWD={password}')
    return cnxn, cnxn.cursor()

def MongoDataReader(tb_name, condition):
    schema = Mongo()
    table = schema[tb_name]
    datas = list(table.find(condition))
    for d in datas:
        del d['_id']
    return datas

def MongoDistinct(tb_name, distinct_h):
    schema = Mongo()
    table = schema[tb_name]
    return list(table.distinct(distinct_h))
    