from importlib import import_module, util
import os
from Config import getConnectionConfig, header
from pymongo import MongoClient
import requests
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): path = os.getcwd()

__updated__ = '2020-11-22 23:22:07'

def crawl_json_data(url):
    res = requests.get(url, headers=header)
    # print(res)
    return res.json()

def import_file_as_module(module_name, file_path):
    """
    import file as module
    """
    spec = util.spec_from_file_location(module_name, file_path)
    foo = util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return foo

def Line():
    LinepyPath = os.path.join(os.path.dirname(path), 'Messenger', 'LineMessenger.py')
    linepy = import_file_as_module('linepy', LinepyPath)
    return linepy.LineMessenger()

def Tele():
    TelepyPath = os.path.join(os.path.dirname(path), 'Messenger', 'TelegramMessenger.py')
    telepy = import_file_as_module('telepy', TelepyPath)
    return telepy.TelegramMessenger()

def Mongo():
    user, password, ip, port = getConnectionConfig()
    return MongoClient(f'mongodb://{user}:{password}@{ip}:{port}')
    
    