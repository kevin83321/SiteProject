from importlib import import_module, util
import os
import time
import requests
parent = os.path.dirname(os.path.abspath(__file__))

if not os.path.isdir(parent): parent = os.getcwd()

__updated__ = '2021-08-26 15:21:46'

header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'upgrade-insecure-requests': '1'}

line_notify_token = "CS5SclcaRvMSmwzR21hNYyPaeQtvDipYpMYgeGajPTT"

def crawl_json_data(url):
    """
    爬取以json格式回傳的url資料，
    """
    try:
        res = requests.get(url, headers=header)
    except Exception as e:
        print(e)
        time.sleep(45)
        return crawl_json_data(url)
    else:
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
    LinepyPath = os.path.join(os.path.dirname(os.path.dirname(parent)), 'Messenger', 'LineMessenger.py')
    linepy = import_file_as_module('linepy', LinepyPath)
    return linepy.LineMessenger()

def Tele():
    TelepyPath = os.path.join(os.path.dirname(os.path.dirname(parent)), 'Messenger', 'TelegramMessenger.py')
    telepy = import_file_as_module('telepy', TelepyPath)
    return telepy.TelegramMessenger()