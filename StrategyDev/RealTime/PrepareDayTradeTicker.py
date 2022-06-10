import shioaji as sj
from pymongo import MongoClient
import json
import os 
from datetime import datetime, timedelta
from Messenger.LineMessenger import LineMessenger as Line
parent = os.path.dirname(os.path.abspath(__file__))
StrongPath = os.path.join(parent, 'StrongTickers')
if not os.path.isdir(StrongPath):
    os.makedirs(StrongPath)
    
from prettytable import PrettyTable

def createSummaryTable(open_thresholds:dict):
    try:
        tickers = []
        high_list = []
        low_list = []
        close_list = []
        for ticker in open_thresholds.keys():
            tickers.append(ticker)
            high_list.append(open_thresholds[ticker]['PreHigh'])
            low_list.append(open_thresholds[ticker]['PreLow'])
            close_list.append(open_thresholds[ticker]['PreClose'])
        table = PrettyTable()
        table.add_column('代號', tickers)
        table.add_column("今高", high_list)
        table.add_column("今低", low_list)
        table.add_column("今收", close_list)
        table.align = 'r'
    except Exception as e:
        print(e)
    else:
        return table

def getTable(setting, schema, table_name):
    try:
        user = setting['user']
        pwd = setting['pwd']
        ip = setting['ip']
        port = setting['port']
        client = MongoClient(f'mongodb://{user}:{pwd}@{ip}:{port}')
        schema = client['admin'][schema]
        table = schema[table_name]
    except:
        pass
    return table

def getFollowedAssets(followedAssets=None):
    try:
        setting = {
            'user':'kevin83321',
            'pwd':'j7629864',
            'ip':'192.168.2.173',
            'port':'49153'
        }
        schema = 'TWSE'
        if followedAssets is None:
            table = getTable(setting, schema,'StockList')
            updateDate = sorted(table.distinct('UpdateDate'))[-1]
            datas = list(table.find({'Industry':{'$ne':''}}))
            return [x['Ticker'] for x in datas if x['UpdateDate'] == updateDate]
    except Exception as e:
        print(e)
        pass
    else:
        return followedAssets

def writeStrongTicker(dtStr, tickers, datapath = None):
    global StrongPath
    if datapath:
        StrongPath = datapath
    try:
        with open(os.path.join(StrongPath, f'{dtStr}_strongTicker.json'), 'w') as f:
            json.dump(tickers,f)

        # with open(os.path.join(StrongPath, f'{dtStr}_strongTicker.txt'), 'w') as f:
        #     json.dump(tickers,f)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    api = sj.Shioaji()
    api.login("F128497445", "89118217k")
    tickers = getFollowedAssets()
    up_limit_ticker = {}
    for ticker in tickers:
        tmp_contract = api.Contracts.Stocks[ticker]
        shot = api.snapshots([tmp_contract])[0]
        if tmp_contract.limit_up == shot.high:
            if shot.total_volume >= 3000:
                if (shot.high / shot.close - 1) <= 0.02:
                    up_limit_ticker[ticker] = {
                        'PreClose':shot.close,
                        'PreHigh':shot.high,
                        'PreLow':shot.low
                    }

    td = datetime.today()
    i = 1
    while True:
        next_trade_day = td + timedelta(i)
        if next_trade_day.isocalendar()[-1] <= 5:
            break
        i += 1
    print(next_trade_day)
    writeStrongTicker(next_trade_day.strftime('%Y-%m-%d'),dict(up_limit_ticker))

    text_table = createSummaryTable(up_limit_ticker)
    text = f'\n【{td.strftime("%Y-%m-%d")}】當沖策略隔日挑選標的\n\n'
    text += text_table.get_string()
    Line.sendMessage(text)