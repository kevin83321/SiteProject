import requests
from LineNotify import WintogLineNotify
from datetime import datetime, timedelta
from time import sleep
from PySQLFunc import executeSQL, GetPKNO, Insert

def crawl_json_data(url, header):
    res = requests.get(url, headers=header)
    return res.json()

def changeIntoSQLForm(data):
    td = datetime.today()
    d, t = td.strftime('%Y/%m/%d %H:%M:%S').split(' ')
    return {
        'UPDATE_USER_ID':"'Kevin'",
        'UPDATE_DATE':f"'{d}'",
        'UPDATE_TIME':f"'{t}'",
        'UPDATE_PROG_CD':"''", 
        'EXCHANGE':"'US'", 
        'ASSETS_TYPE':"'STOCK'", #  if data['AssetType'] == '股票' else f"'{data['AssetType']}'", #data['AssetType'] 
        'SYMBOL_CODE':f"'{data['symbol']}'", 
        'SYMBOL_ATTR':"'Listed'", 
        'SYMBOL_NAME':f"'{' '.join(data['name'].split(' ')[:2])}'".replace("Corporation", "Corp.").split(',')[0]+"\'", 
        'IS_ORDER':1, 
        'PUBLIC_DATE':"''", # f"'{data['IssueDate'].replace('-', '/')}'"
        'INDUSTRY':f"'{data['INDUSTRY']}'", 
    }

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

def GetEquityProfile(data):
    # sub stock profile
    symbol = data["symbol"]
    profile_url_root = f'https://api.nasdaq.com/api/company/{symbol}/company-profile'
    headers_profile = {
        'authority': 'api.nasdaq.com',
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
    profile_data = crawl_json_data(profile_url_root, headers_profile)
    profile_detail = profile_data['data']
    return {'INDUSTRY': profile_detail['Sector']['value'] if profile_detail != None else ""}

def InsertSQLInfo(datas):
    temp_k = None
    for data in datas:
        if not temp_k:
            temp_k = list(data.keys())
            k_str = ', '.join(temp_k)
        v_str = ', '.join([str(data[k]) for k in temp_k])
        Insert(db = 'MARKET101', k_str=k_str, v_str=v_str)

def UpdateInfo():
    rows = GetListedEquity()
    datas = []
    for data in rows:
        try:
            data.update(GetEquityProfile(data))
            datas.append(changeIntoSQLForm(data))
            sleep(1)
        except Exception as e:
            print(e)
    InsertSQLInfo(datas)

if __name__ == '__main__':
    UpdateInfo()