from pandas import DataFrame, concat, date_range
from bs4 import BeautifulSoup as bs
import re, time, json, requests
from datetime import timedelta, datetime
from numpy import unique

header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'upgrade-insecure-requests': '1'}

def changeType(k, v):
        # k = col_map.get(k, k)
        if k in '名稱,代號,持股資料月份'.split(','):
            return (k, v)
        try:
            v = float(v.replace(',', ''))
        except:
            v = float('nan')
        return (k, v)

def crawl_data(rank=0):
    url = 'https://goodinfo.tw/StockInfo/StockList.asp?SEARCH_WORD=&SHEET=%E8%91%A3%E7%9B%A3%E6%8C%81%E8%82%A1&SHEET2=&MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E5%85%A8%E9%AB%94%E8%91%A3%E7%9B%A3%E8%B3%AA%E6%8A%BC%E6%AF%94%E4%BE%8B%28%25%29%40%40%E5%85%A8%E9%AB%94%E8%91%A3%E7%9B%A3%40%40%E8%B3%AA%E6%8A%BC%E6%AF%94%E4%BE%8B%28%25%29&STOCK_CODE=&RANK=0&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99&STEP=DATA&SORT_FIELD=%E5%85%A8%E9%AB%94%3Cbr%3E%E8%91%A3%E7%9B%A3%3Cbr%3E%E8%B3%AA%E6%8A%BC%3Cbr%3E%28%25%29&SORT=DOWN'
    payload = {'SEARCH_WORD': '',
                'SHEET': '董監持股',
                'SHEET2': '',
                'MARKET_CAT': '熱門排行',
                'INDUSTRY_CAT': '全體董監質押比例(%)@@全體董監@@質押比例(%)',
                'STOCK_CODE': '',
                'RANK': f'{rank}',
                'RPT_TIME': '最新資料',
                'STEP': 'DATA',
                'SORT_FIELD': '全體<br>董監<br>質押<br>(%)',
                'SORT': 'DOWN',
                }
    header.update({
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-length': '0',
            'content-type': 'application/x-www-form-urlencoded;',
            'cookie': 'CLIENT%5FID=20201116001954608%5F111%2E251%2E82%2E173; _ga=GA1.2.1414533799.1605457214; __gads=ID=836e644d92766719:T=1605457213:S=ALNI_MZwZ5gdWTVfj8yWmAb2AN6Bm808hg; SCREEN_SIZE=WIDTH=1920&HEIGHT=1080; _gid=GA1.2.1198414222.1606577590',
            'origin': 'https://goodinfo.tw',
            'referer': 'https://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E5%85%A8%E9%AB%94%E8%91%A3%E7%9B%A3%E8%B3%AA%E6%8A%BC%E6%AF%94%E4%BE%8B%28%25%29%40%40%E5%85%A8%E9%AB%94%E8%91%A3%E7%9B%A3%40%40%E8%B3%AA%E6%8A%BC%E6%AF%94%E4%BE%8B%28%25%29&SHEET=%E8%91%A3%E7%9B%A3%E6%8C%81%E8%82%A1&selRank=1',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
    })

    
    res = requests.post(url, headers=header, data=payload)
    # /html/body/table[5]/tbody/tr/td[3]/div[2]/div/div/table[1]
    # print(js)
    res.encoding = 'big5'
    soup = bs(res.content, 'lxml')
    table = soup.find_all('table')[1]#.find_all('table')
    # print(table)
    # table = 
    cols = [x.text.strip() for x in table.find_all('thead')[1].find_all('tr')[0].find_all('td')]
    cols[-1] = cols[-1][:-2]
    datas = table.find_all('tr')
    full_dict = []
    for data in datas:
        tds = [x.text.strip() for x in data.find_all('td')]
        if cols != tds:
            full_dict.append(dict(changeType(k, v) for k,v in zip(cols, tds)))
    return full_dict

def main():
    datas = []
    for rank in range(6):
        datas.extend(crawl_data(rank))
    return datas

if __name__ == '__main__':
    print(main())