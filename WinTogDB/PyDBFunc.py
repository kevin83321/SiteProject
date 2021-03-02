# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.28
# Update: Create
# Version: 1

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from pymongo import MongoClient

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