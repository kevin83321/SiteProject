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

@app.route('/Api/Quote/Daily/Stock', methods=['GET','POST'])
def get():
    params = {
        'Ticker':None,
        'startDate':None,
        'endDate':None
    }
    for key in params.keys():
        if key not in request.args: return jsonify({'msg':f'{key} 不存在', 'GridData':{}})
        params[key] = request.args[key]
    Data = MongoDB.get('TWSE', 'historicalPrice', **params)
    for data in Data: del data['_id']
    return jsonify({'msg':f'成功取得資料 {params["Ticker"]} form {params["startDate"]} to {params["endDate"]}','GridData':Data})

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


if __name__ == "__main__":
    app.config["DEBUG"] = True
    serve(app, host='localhost', port=8080, threads=4)