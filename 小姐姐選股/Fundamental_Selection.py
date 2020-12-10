# Create : 2020-12-04

__updated__ = '2020-12-06 22:27:55'

from pymongo import MongoClient
from ShareHolder import main as ShareHolder
from ReturnofEquity import main_near4 as ReturnofEquity
from ReturnofEquity import main_near12 as ReturnofEquity_near12
from datetime import datetime, timedelta
from itertools import product
from pandas import DataFrame

def final_publish_date(year):
    return  [datetime(year, 3, 31),
             datetime(year, 5, 15),
             datetime(year, 8, 14),
             datetime(year, 11, 14)]
    
def getStartEnd(publish_dates):
    try:
        firstQ, lastQ = publish_dates[0], publish_dates[-1]
        start_date = datetime(firstQ[0], firstQ[1]*3-2, 1)
        if lastQ[1]*3 == 12:
            end_date = datetime(lastQ[0]+1, 1, 1)
        else:
            end_date = datetime(lastQ[0], lastQ[1]*3+1, 1)
    except Exception as e:
        print(e)
    else:
        return start_date, end_date
    
def GetLastNQuarters(today = datetime.today()):
    try:
        publish_dates = final_publish_date(today.year)
        Quarter = -1
        Quarter += sum([today >= publish_date for publish_date in publish_dates])
        quarters = [(Y, Q) for Y, Q in product(range(today.year - 1, today.year), range(Quarter+1, 5))]
        if Quarter:
            quarters.extend([(Y, Q) for Y, Q in product(range(today.year, today.year + 1), range(1, Quarter+1))])
    except Exception as e:
        print(e)
    else:
        return quarters

def Getdb(db_name):
    try:
        # client = MongoClient('mongodb://kevin:j7629864@localhost:27017')
        client = MongoClient('mongodb://xiqi:xiqi2018@220.135.204.227:27017')
        schema = client['admin']
        db = schema['TWSE'][db_name]
    except Exception as e:
        print(e)
    else:
        return db

def getStockList():
    try:
        db = Getdb('StockList')
        updateDate = sorted(db.distinct('UpdateDate'))[-1]
        data = list(db.find({'UpdateDate':{'$eq':updateDate}, 'Industry':{'$ne':''}}))
    except Exception as e:
        print(e)
    else:
        return [x['Ticker'].strip() for x in data]

def getFundamental(tickers):
    try:
        db = Getdb('Fundmental')
        quarters = GetLastNQuarters()
        data = []
        for Y, Q in quarters:
            data.extend(list(db.find({'Ticker':{'$in':tickers}, 'Year':{'$eq':str(Y)}, 'Quarter':{'$eq':str(Q)}})))
    except Exception as e:
        print(e)
    else:
        return data
    
def getLastPrice(tickers, end):
    try:
        # tickers = getStockList()
        db = Getdb('historicalPrice')
        last_date = sorted(db.distinct('Date'))[-1]
        start = end - timedelta(days=31)
        df = DataFrame(list(db.find({'Date':{'$gte':start.strftime('%Y-%m-%d'), '$lte':last_date}, 'Ticker':{'$in':tickers}})))
        df = df.replace('--', float('nan')).replace('----', float('nan'))
        last_prices = {}
        for ticker in df.Ticker.unique():
            temp = df[df.Ticker==ticker].fillna(method='ffill')
            try:
                last_prices[ticker] = temp[temp.Date == last_date].Close.values[0]
            except:
                pass
    except Exception as e:
        print('LastPrice', e)
    else:
        return last_prices

def getHolderStatus(tickers):
    """
    取得董監事持股狀態與質押比
    """
    status = ShareHolder()
    return dict((x['代號'], {'持股':x['全體董監持股(%)'], '質押比':x['全體董監質押(%)']}) for x in status if x['代號'] in tickers)

def CashYield(tickers, start_date, end_date):
    """
    計算現金殖利率
    現金殖利率 = 配息(元) / 股價(元)
    　　　　　 = (發放現金股利 / 1000) / 股價(元)
    配息 = 現金股利 / 1000 (發放現金股利)
    """
    try:
        final_data = {}
        lastPrices = getLastPrice(tickers, end_date)
        db = Getdb('Actions')
        actions = list(db.find({'Ticker':{'$in':tickers}, 'Date':{'$gte':start_date.strftime('%Y-%m-%d'), '$lte':end_date.strftime('%Y-%m-%d')}}))
        for ticker in tickers:
            try:
                cashdividends = sum([x['Value'] for x in actions if x['Ticker'] == ticker and x['Action'] == 'XD'])
                final_data[ticker.strip()] = cashdividends / lastPrices[ticker]
            except:
                pass
    except Exception as e:
        print('Cash Yield', e)
    else:
        return final_data

def DebtRatio(tickers, data):
    """
    計算負債比
    負債比 = 總負債 / 總資產
    　　　 = 負債總額 / 資產總額
    """
    try:
        final_data = {}
        lastQ = GetLastNQuarters()[-1]
        data = [x for x in data if x['Year'] == str(lastQ[0]) and x['Quarter'] == str(lastQ[1])]
        for x in data:
        # for ticker in tickers:
            last_data = x['資產負債表']
            total_equity = last_data['資產總計']['Value']
            total_debt = last_data['負債總計']['Value']
            final_data[x['Ticker']] = total_debt / total_equity
    except Exception as e:
        print('DebtRatio', e)
    else:
        return final_data

def GetROE(tickers):
    """
    計算ROE
    ROE = Return of Equity
        = 稅後淨利 / 權益總額
    """
    datas = ReturnofEquity()
    return [(x['代號'], x['ROE(%)']) for x in datas if x['代號'] in tickers]

def GetROE_near12(tickers):
    """
    計算ROE
    ROE = Return of Equity
        = 稅後淨利 / 權益總額
    """
    datas = ReturnofEquity_near12()
    cols = sorted([col for col in datas[0].keys() if 'Q' in col])
    final_data = {}
    for data in datas:
        last_3_cum = round(sum([data[col] for col in cols[-6:-2]]), 2)
        last_2_cum = round(sum([data[col] for col in cols[-5:-1]]), 2)
        last_1_cum = round(sum([data[col] for col in cols[-4:]]), 2)
        final_data[data['代號']] = dict((col[:7]+'_cum', cum) for col, cum in zip(cols[-3:], [last_3_cum, last_2_cum, last_1_cum]))
    return final_data

#############################################
## Filter Functions
#############################################

def YieldFilter(data):
    """
    挑選現金殖利率 >= 4%
    """
    return [ticker for ticker, y in data.items() if y >= 0.05]

def DebtFilter(data):
    """
    挑選負債比 < 50%
    """
    return [ticker for ticker, debtratio in data.items() if debtratio <= 0.5]

def ROEFilter(data):
    """
    挑選ROE > 5%
    """
    return [ticker for ticker, roe in data if roe >= 5]

def ROEFilter_near12(data):
    """
    挑選ROE > 5%
    """
    final = []
    for ticker, roes in data.items():
        if all([roe >= 5 for k, roe in roes.items()]):
            final.append(ticker)
    return final

def HolderFilter(data, hold_percent=20):
    """
    持股比率需 > 20%
    董監持股質押比例 = 董監持股質押張數 / 總股數
    """
    return dict((ticker, holding) for ticker, holding in data.items() if holding['持股'] >= hold_percent)
    
def main_raw_rule():
    tickers = getStockList()
    start_date, end_date = getStartEnd(GetLastNQuarters())
    fund_data = getFundamental(tickers)
    
    # 計算現金殖利率，並過濾
    CashYields = CashYield(tickers, start_date, end_date)
    YieldFilted = YieldFilter(CashYields)
    # print('\nYieldFilted', YieldFilted)
    
    # # 計算負債比，並過濾
    DebtRatios = DebtRatio(tickers, fund_data)
    DebtFilted = DebtFilter(DebtRatios)
    # print('\nDebtFilted', DebtFilted)
    
    # # 爬取ROE，並過濾
    ROEs = GetROE(tickers)
    ROEFilted = ROEFilter(ROEs)
    # print('\nROEFilted', ROEFilted)
    
    # 董監持股比、質押比
    holders_Status = getHolderStatus(tickers)
    HolderFilted = HolderFilter(holders_Status, 10)
    print('\nHolderFilted', list(HolderFilted.keys()))
    
    final_tickers = set(YieldFilted).intersection(DebtFilted)
    print('\nintersect Yield and Debt', final_tickers)
    final_tickers = final_tickers.intersection(ROEFilted)
    print('\nintersect Yield and Debt and ROE', final_tickers)
    final_tickers = final_tickers.intersection(list(HolderFilted.keys()))
    print('\nintersect Yield and Debt and ROE and holdings', final_tickers)
    print(sorted([(ticker, HolderFilted[ticker]['質押比']) for ticker in final_tickers], key=lambda x: x[1]))
    
def main_new_rule1():
    tickers = getStockList()
    today = datetime.today()
    start_date, end_date = getStartEnd(GetLastNQuarters(today))
    # fund_data = getFundamental(tickers)
    
    # 計算現金殖利率，並過濾
    CashYields_1 = CashYield(tickers, start_date, end_date)
    CashYields_2 = CashYield(tickers, *getStartEnd(GetLastNQuarters(datetime.today() - timedelta(20*3))))
    CashYields_3 = CashYield(tickers, *getStartEnd(GetLastNQuarters(datetime.today() - timedelta(20*6))))
    YieldFilted_1 = YieldFilter(CashYields_1)
    YieldFilted_2 = YieldFilter(CashYields_2)
    YieldFilted_3 = YieldFilter(CashYields_3)
    YieldFilted = set(YieldFilted_1).intersection(YieldFilted_2).intersection(YieldFilted_2)
    # print('\nYieldFilted', YieldFilted)
    
    # # 計算負債比，並過濾
    # DebtRatios = DebtRatio(tickers, fund_data)
    # DebtFilted = DebtFilter(DebtRatios)
    # print('\nDebtFilted', DebtFilted)
    
    # # 爬取ROE，並過濾
    ROEs = GetROE_near12(tickers)
    ROEFilted = ROEFilter_near12(ROEs)
    # print('\nROEFilted', ROEFilted)
    
    # 董監持股比、質押比
    # holders_Status = getHolderStatus(tickers)
    # HolderFilted = HolderFilter(holders_Status, 10)
    # print('\nHolderFilted', list(HolderFilted.keys()))
    
    final_tickers = set(YieldFilted).intersection(ROEFilted)
    print(final_tickers)
    # print(sorted([(ticker, HolderFilted[ticker]['質押比']) for ticker in final_tickers], key=lambda x: x[1]))
    
if __name__ == '__main__':
    # main_raw_rule()
    # print(GetROE_near12(getStockList()))
    main_new_rule1()
    
    