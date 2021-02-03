from modules import Tele, Mongo
from CloseAdjusted import getDataWithAdjClose
from datetime import datetime, timedelta
import os, time
from concurrent.futures import ThreadPoolExecutor

__updated__ = '2021-01-30 13:00:17'

def update_one(table, x): 
    try:
        table.update_one({'_id':x['_id']}, {'$set':x}, upsert=True)
    except KeyboardInterrupt:
        os._exit(0)
    except Exception as e:
        print(e)
        pass
    
def update_data(d):
    del d['Index']
    d['Adj Close'] = d.pop('Adj_Close')
    d['_id'] = d.pop('idx')
    d['Date'] = d.pop('Date').strftime('%Y-%m-%d')
    return d
    
def updateAdjusted(row, client, table):
    ticker = row['Ticker'].strip(); start_date = row['IssueDate']; end = row['UpdateDate']
    try:
        data = getDataWithAdjClose(client, ticker, 'TWSE', start_date, end)
        data['Ticker'] = ticker
        data.index.name = 'Date'
        data = data.reset_index()
        data.rename(columns={'_id':'idx', 'Adj Close':'Adj_Close'}, inplace=True)
        datas = [dict(x._asdict()) for x in data.itertuples()]
        with ThreadPoolExecutor(20) as executor:
            exes = [executor.submit(update_data, d) for d in datas]
            datas = [exe.result() for exe in exes]            
    except Exception as e:
        print(e)
        pass
    except KeyboardInterrupt:
        os._exit(0)
    else:
        with ThreadPoolExecutor(20) as executor:
            results = [executor.submit(update_one, table, data) for data in datas]
            [res.result() for res in results]
        Tele.sendMessage(f'update Adj Close of {ticker} Success')
        return 
    Tele.sendMessage(f'update Adj Close of {ticker} Failed')

if __name__ == '__main__':
    # Connect to Mongo
    client = Mongo()

    # connect to historical Price table
    table = client['admin']['TWSE']['historicalPrice']
    uniqueStock = table.distinct('Ticker') 

    # connect to stocklist table
    tickers_table = client['admin']['TWSE']['StockList']
    updateDate = sorted(tickers_table.distinct('UpdateDate'))[-1]

    # get all tickers
    tickers = list(tickers_table.find({'UpdateDate':{'$eq':updateDate}}))
    # tickers = list(tickers_table.find())

    # create pool and run update Adjusted Close
    start_time = time.time()
    with ThreadPoolExecutor(20) as executor:
        exes = [executor.submit(updateAdjusted, row, client, table) for row in [row for row in tickers if row['Ticker'] in uniqueStock]]
        finished_process = [exe.result() for exe in exes]
    duration = round((time.time() - start_time) / 3600, 4)
    Tele().sendMessage(f'update {len(finished_process)} assets, used {duration} hours', group='UpdateMessage')
