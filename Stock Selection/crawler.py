import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import json
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
          'Content-Type': 'application/json;charset=UTF-8'}

def parse_json_data(d):
    return {
            '商品':d['DispCName'],
            '買價':d['CBidPrice1'].replace(',','').strip(),
            '買量':d['CBidSize1'].replace(',','').strip(),
            '賣價':d['CAskPrice1'].replace(',','').strip(),
            '賣量':d['CAskSize1'].replace(',','').strip(),
            '成交價':d['CLastPrice'].replace(',','').strip(),
            '漲跌':d['CDiff'].replace(',','').strip(),
            '漲跌幅':d['CDiffRate'].replace(',','').strip()+"%",
            '振幅':d['CAmpRate'].replace(',','').strip()+"%",
            '成交量':d['CTotalVolume'].replace(',','').strip(),
            '開盤':d['COpenPrice'].replace(',','').strip(),
            '最高':d['CHighPrice'].replace(',','').strip(),
            '最低':d['CLowPrice'].replace(',','').strip(),
            '參考價':d['CRefPrice'].replace(',','').strip(),
            }

def getIdxFuture():
    try:
        url = 'https://mis.taifex.com.tw/futures/api/getQuoteList'
        payloads = json.dumps({"MarketType":"0","SymbolType":"F","KindID":"1","CID":"","ExpireMonth":"","RowSize":"全部","PageNo":"","SortColumn":"","AscDesc":"A"})
        res = requests.post(url, data=payloads, headers=header)
        
        js = res.json()
        data = js['RtData']['QuoteList']
        final_data = []
        for d in data:
            final_data.append(parse_json_data(d))
        return final_data
    except Exception as e:
        print(f'In getIdxFuture, Error : {e}')
        return None, None
    
def getTaiFut():
    final_data = getIdxFuture()
    Last_TaiFut = [x for x in final_data if '臺指期' in x['商品'] and '小' not in x['商品']][0]
    return float(Last_TaiFut['參考價']), float(Last_TaiFut['成交價'])

if __name__ == '__main__':
    print(getTaiFut())