import requests
from LineNotify import WintogLineNotify
from PyCasFunc import CassandraInsert

def crawl_json_data(url, header):
    res = requests.get(url, headers=header)
    return res.json()

def changeToFloat(x):
    try:
        return float(str(x).replace(',','').replace('$',''))
    except:
        return x
    
def Update_data_dict(data):
    for k in data.keys():
        data[k] = changeToFloat(data[k])
    return data

def ChangeIntoCasForm(data, asset_type, ticker):
    update_date, update_time = datetime.today().strftime('%Y/%m/%d %H:%M:%S').split(' ')
    m, d, y = data['date'].split('/')
    trade_date = '/'.join([y, m, d])
    return {
        'exchange': 'US',
        'assets_type': 'Stock', # if asset_type == '股票' else 'ETF',
        'symbol_code': ticker,
        'kline_period': '1440',
        'kline_datetime': trade_date, # data['Date'].replace('-', '/'),
        'close_price': str(data['close']),
        'high_price': str(data['high']),
        'low_price': str(data['low']),
        'open_price': str(data['open']),
        'pkno': None,
        'trans_volume': str(data['volume']),
        'update_date': update_date,
        'update_time': update_time,
        'update_user_id': 'Kevin',
    }

def GetHitoricalPrice(equity, updated_date):
    # start_date = "2010-01-01" # 1971-02-05
    # end_date = "2021-07-29"
    start_date = updated_date.strftime("%Y-%m-%d")
    symbol = equity['symbol'] # "AAPL"
    url = f"https://api.nasdaq.com/api/quote/{symbol}/historical?assetclass=stocks&fromdate={start_date}&limit=18&todate={end_date}"

    headers = {
        'authority': 'api.nasdaq.com',
        'method': 'GET',
    #     'path': '/api/quote/AAPL/historical?assetclass=stocks&fromdate=2011-07-29&limit=18&todate=2021-07-29',/
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.nasdaq.com',
        'referer': 'https://www.nasdaq.com/',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    }

    js = crawl_json_data(url, headers=headers)
    return js['data']['tradesTable']['rows']


def GetListedEquity():
    # list data
    headers = {
        'authority': 'api.nasdaq.com',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    }

    url = 'https://api.nasdaq.com/api/screener/stocks?tableonly=false&limit=0&offset=0'
    data = crawl_json_data(url, headers)
    return data['data']['table']['rows']

def Update():
    ListEquity = GetListedEquity()
    for equity in ListEquity:
        rows = GetHitoricalPrice()
    ChangeIntoCasForm(Update_data_dict(rows[0]), "Stock", symbol)