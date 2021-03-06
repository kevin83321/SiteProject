from pandas import DataFrame, concat, date_range
from bs4 import BeautifulSoup as bs
import re, time, json, requests
from datetime import timedelta, datetime
from numpy import unique

header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'upgrade-insecure-requests': '1'}

def changeType(k, v):
        # k = col_map.get(k, k)
        if k in '名稱,代號,財報季度'.split(','):
            return (k, v)
        try:
            v = float(v.replace(',', ''))
        except:
            v = float('nan')
        return (k, v)

def crawl_data(rank=0):
    url = 'https://goodinfo.tw/StockInfo/StockList.asp?SEARCH_WORD=&MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E5%B9%B4%E5%BA%A6%E7%A8%85%E5%BE%8C%E6%B7%A8%E5%88%A9%E6%9C%80%E9%AB%98%40%40%E7%A8%85%E5%BE%8C%E6%B7%A8%E5%88%A9%40%40%E5%B9%B4%E5%BA%A6%E7%A8%85%E5%BE%8C%E6%B7%A8%E5%88%A9%E6%9C%80%E9%AB%98&STOCK_CODE=&RANK=0&STEP=DATA&SHEET=%E8%BF%91%E5%9B%9B%E5%AD%A3%E7%8D%B2%E5%88%A9%E8%83%BD%E5%8A%9B'
    payload = {'SEARCH_WORD': '',
                'SHEET': '近四季獲利能力',
                'SHEET2': '',
                'MARKET_CAT': '熱門排行',
                'INDUSTRY_CAT': '年度稅後淨利最高@@稅後淨利@@年度稅後淨利最高',
                'STOCK_CODE': '',
                'RANK': f'{rank}',
                'RPT_TIME': '最新資料',
                'STEP': 'DATA',
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

def crawl_data_near12(rank):
    url = 'https://goodinfo.tw/StockInfo/StockList.asp?SEARCH_WORD=&SHEET=%E5%AD%A3%E7%B4%AF%E8%A8%88%E7%8D%B2%E5%88%A9%E8%83%BD%E5%8A%9B%5F%E8%BF%91N%E5%AD%A3%E4%B8%80%E8%A6%BD&MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E5%B9%B4%E5%BA%A6%E7%A8%85%E5%BE%8C%E6%B7%A8%E5%88%A9%E6%9C%80%E9%AB%98%40%40%E7%A8%85%E5%BE%8C%E6%B7%A8%E5%88%A9%40%40%E5%B9%B4%E5%BA%A6%E7%A8%85%E5%BE%8C%E6%B7%A8%E5%88%A9%E6%9C%80%E9%AB%98&STOCK_CODE=&RANK=0&STEP=DATA&SHEET2=ROE(%25)'
    payload = {'SEARCH_WORD': '',
                'SHEET': '季累計獲利能力_近N季一覽',
                'SHEET2': 'ROE(%)',
                'MARKET_CAT': '熱門排行',
                'INDUSTRY_CAT': '年度稅後淨利最高@@稅後淨利@@年度稅後淨利最高',
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

def main_near4():
    datas = []
    for rank in range(6):
        datas.extend(crawl_data(rank))
        time.sleep(3)
    return datas

def main_near12():
    datas = []
    for rank in range(6):
        datas.extend(crawl_data_near12(rank))
        time.sleep(3)
    return datas

if __name__ == '__main__':
    print(main_near4())