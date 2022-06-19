from pandas import DataFrame, to_datetime
from datetime import datetime, timedelta
from utils import getSchema, changedType

def StockInterDay(start_date:[str,datetime]=datetime(2021,4,14), 
                  end_date:[str,datetime]=datetime(2021,4,14),
                  tickers:[str,list]=''):
    if isinstance(start_date, datetime):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, datetime):
        end_date = end_date.strftime("%Y-%m-%d")
    if isinstance(tickers, str):
        tickers = tickers.split(',')
    schema = getSchema('TWSE')
    table = schema['historicalPrice']
    data = list(table.find({'Date':{'$gte':start_date, '$lte':end_date}, "Ticker" :{"$in":tickers}}))
    if data:
        df = DataFrame(data)
        df.Date = to_datetime(df.Date)
        for col in 'Open,High,Low,Close,Volume'.split(','):
            df[col] = df[col].apply(changedType)
        return df
    return data

def StockList():
    schema = getSchema('TWSE')
    table = schema['StockList']
    last_date = sorted(table.distinct("UpdateDate"))[-1]
    data = list(table.find({"UpdateDate":{"$eq":last_date}, "Industry" :{"$ne":""}}))
    return data

def get_commission(price:float, multiplier:int=1000, qty=1, long:bool=1, dayTrade:bool=False):
    """
    計算個別部位的單邊交易成本

    Params:
        symbol : 商品代碼
        exchange : 交易所
        cost : 交易價格
        multiplier : 價格還原現金之乘數
            例如:
                股票 : 1張 = 1,000股，10元的股票還原現金價值，即為10 *1,000 = 10,000元
                期貨 : 台指期1點200元，假設現在10,000點，則一口台股的價值為 200 * 10,000 = 2,000,000
        qty : 買賣口數或張數
        Real : 是否為實單, default = False
        direction : 交易方向 進場(買賣)或出場
            P.S. 股票交易的交易稅是出場才計算
    """
    commission = price * (0.1425 / 100) * multiplier * qty
    commission = 20 if commission < 20 else commission
    tax = price * (0.3 / 100) * multiplier * qty
    if dayTrade:
        fee /= 2
#     tradeCost = commission# * 0.6
    if not long:
        return commission, tax
    return commission, 0

def CreateTradeLog(entry_date, exit_date, entry_price, exit_price, max_price, min_price, pos:int = 1, qty:int = 1, multiplier:int=1000):
    pnl = (exit_price - entry_price) * pos * qty * multiplier
    entry_com, entry_tax = get_commission(entry_price, multiplier, qty, long = pos > 0)
    exit_com, exit_tax = get_commission(exit_price, multiplier, qty, long = not (pos > 0))
#     print(entry_date, exit_date, entry_price, exit_price,entry_com,entry_tax,exit_com,exit_tax)
    return {
        'EntryDate':entry_date,
        'ExitDate':exit_date,
        'EntryPrice':entry_price,
        'ExitPrice':exit_price,
        'EntryCommission':round(entry_com),
        'ExitCommission':round(exit_com),
        'EntryTax':round(entry_tax),
        'ExitTax':round(exit_tax),
        'TotalCost':round(entry_com)+round(exit_com)+round(entry_tax)+round(exit_tax),
        'HoldingPeriod':(exit_date-entry_date).days,
        'Net':round(pnl - (round(entry_com)+round(exit_com)+round(entry_tax)+round(exit_tax))),
        'Ret':round((pnl - (round(entry_com)+round(exit_com)+round(entry_tax)+round(exit_tax))) / (entry_price * 1000),4),
        'MaxPriceBetweeenHolding':max_price,
        'MaxRetBetweeenHolding':round(max_price/entry_price-1,4),
        'MinPriceBetweeenHolding':min_price,
        'MinRetBetweeenHolding':round(min_price/entry_price-1,4)
    }

def Backtest(strategy:callable, ticker:str, dt:datetime=datetime.today(), bt_period = 5, params:dict={}):
    df = StockInterDay(dt+timedelta(-365*bt_period), dt, ticker)
    if isinstance(df, list):
        if not df: return []
    if df.empty: return []
    return strategy(df, **params)
    