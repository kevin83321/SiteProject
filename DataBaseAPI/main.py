# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.06.06
# Update: 2020.06.06
# Version: Test
# !flask/bin/python

from waitress import serve
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from gevent.pywsgi import WSGIServer
import json, os, schedule, time, threading
from datetime import datetime, timedelta
from MongoDB import MongoDB

# setup relative path
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): path = os.getcwd()

# setup web app
app = Flask(__name__)
#FreqMap = {'0':'TICK','1':'1MIN','2':"DAILY"}
@app.route('/Api/Quote/TWSE/DAILY', methods=['GET','POST'])
def getTWSEDaily():
    """
    取得股票日資料
    """
    try:
        params = {
            'Ticker':None,
            'StartDate':None,
            'EndDate':None
        }
        for key in params.keys(): params[key] = request.args[key]
        params.update({'table_name':'historicalPrice', 'db_name':'TWSE'})
        return getDailyPrice(params)
    except Exception as e:
        print(e)

@app.route('/Api/Quote/TWSE/INTRADAY', methods=['GET', 'POST'])
def getTWSEIntraday():
    """
    取得股票日內資料，來源:群益API
    """
    FreqMap = {'0':'Tick', '1':'1MIN'}

@app.route('/Api/Quote/TAIFEX/DAILY', methods=['GET', 'POST'])
def getTAIFEXDaily():
    """
    取得期貨/選擇權日資料
    """
    try:
        params = {
            'Ticker':None,
            'StartDate':None,
            'EndDate':None
        }
        for key in params.keys(): params[key] = request.args[key]
        params.update({'table_name':'historicalPrice', 'db_name':'TAIFEX'})
        return getDailyPrice(params)
    except Exception as e:
        print(e)

@app.route('/Api/Quote/TAIFEX/INTRADAY', methods=['GET', 'POST'])
def getTAIFEXIntraday():
    """
    取得期貨/選擇權日內資料
    """
    FreqMap = {'0':'Tick', '1':'1MIN'}
    

@app.route('/Api/Quote/USSE/INTRADAY', methods=['GET', 'POST'])
def getUSSEDaily():
    """
    取得美國股票日資料
    """
    try:
        params = {
            'Ticker':None,
            'StartDate':None,
            'EndDate':None
        }
        for key in params.keys(): params[key] = request.args[key]
        params.update({'table_name':'historicalPrice', 'db_name':'USSE'})
        return getDailyPrice(params)
    except Exception as e:
        print(e)

@app.route('/Api/Help', methods=['GET', 'POST'])
def help():
    msg = {
        'Api/Quote/Daily/Stock':'',
        'Api/Quote/Daily/Future':'',
    }
    return msg
@app.route('/')
def index():
    return 'this is index page'

def getDailyPrice(params):
    Data = MongoDB.get(**params)
    if isinstance(Data, list):
        for data in Data: del data['_id']
        endDate = max([temp.get('Date') for temp in Data])
        startDate = min([temp.get('Date') for temp in Data])
        return jsonify({'ReplyMsg':f'取得資料成功 {params["Ticker"]} from {startDate} to {endDate}','GridData':Data})
    elif isinstance(Data, str):
        return jsonify({'ReplyMsg':f'取得資料失敗 {params["Ticker"]} from {params["StartDate"]} to {params["EndDate"]}','GridData':Data})

def getTickPrice(params):
    pass

def get1MinPrice(params):
    pass

if __name__ == "__main__":
    app.config["DEBUG"] = True
    serve(app, host='localhost', port=8080, threads=4)