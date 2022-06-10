import os
from prettytable import PrettyTable
import json

parent = os.path.dirname(os.path.abspath(__file__))
StrongPath = os.path.join(parent, 'StrongTickers')
if not os.path.isdir(StrongPath):
    os.makedirs(StrongPath)
trade_result_path = os.path.join(parent, "TradeRecord")
if not os.path.isdir(trade_result_path):
    os.makedirs(trade_result_path)

def readStrongTicker(dtStr):
    global StrongPath
    if os.path.isfile(os.path.join(StrongPath, f'{dtStr}_strongTicker.json')):
        with open(os.path.join(StrongPath, f'{dtStr}_strongTicker.json'), 'r') as f:
            tickers = json.load(f)
            return tickers
    else:
        return {}

def writeTradableTicker(dtStr, tickers):
    global StrongPath
    with open(os.path.join(StrongPath, f'{dtStr}_tradableTicker.json'), 'w') as f:
        json.dump(tickers,f)
        
def createTradableTable(open_thresholds:dict, max_size_map:dict):
    try:
        tickers = []
        max_pos_list = []
        close_list = []
        for ticker in open_thresholds.keys():
            tickers.append(ticker)
            close_list.append(open_thresholds[ticker]['PreClose'])
            max_pos_list.append(max_size_map[ticker])
        table = PrettyTable()
        table.add_column('代號', tickers)
        table.add_column("昨收", close_list)
        table.add_column("最大倉位", max_pos_list)
        table.align = 'r'
    except Exception as e:
        print(e)
    else:
        return table
