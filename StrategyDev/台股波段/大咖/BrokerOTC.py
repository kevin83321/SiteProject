import requests
from bs4 import BeautifulSoup as bs
import json
import os
from time import sleep
from pandas import DataFrame
from datetime import datetime
from numpy import random
parent = os.path.dirname(os.path.abspath('__file__'))

Cookies = [
    '_ga=GA1.3.85183079.1629005206; _gid=GA1.3.706517529.1629005206',
    '_ga=GA1.3.733639354.1628851568; _gid=GA1.3.1064361284.1628851568',
    '_ga=GA1.3.1977008143.1629006706; _gid=GA1.3.1447127669.1629006706'
]
proxies = {
  "http": "http://49.156.33.101:5678",
  "https": "https://49.156.33.101:5678",
}

from lxml.html import fromstring
from itertools import cycle
import traceback
import re

######################FIND PROXIES#########################################
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:299]:   #299 proxies max
        proxy = ":".join([i.xpath('.//td[1]/text()') 
        [0],i.xpath('.//td[2]/text()')[0]])
        proxies.add(proxy)
    return proxies

def GetToken(rs):
    pageurl = 'https://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php?l=zh-tw'

    res = rs.get(pageurl)
    soup = bs(res.text, 'lxml')
    googlekey = soup.select_one('.g-recaptcha').get('data-sitekey')
    g_token_url = f'https://www.google.com/recaptcha/api2/anchor?ar=1&k={googlekey}&co=aHR0cHM6Ly93d3cudHBleC5vcmcudHc6NDQz&hl=zh-TW&v=tFhBvPrftr7Y91fo1S1ASkA6&size=normal&cb=pmwrdg8dc3fi'
    res2 = rs.get(g_token_url)
    soup = bs(res2.text, 'lxml')
    return soup.find_all('input')[0].get("value")

def GetData(rs, ticker='3105', output_path=""):
    token = GetToken(rs)

    url = 'https://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php?l=zh-tw'
    date = datetime.today()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '27',
        'Content-Type': 'application/x-www-form-urlencoded',
    #     'Cookie': '_ga=GA1.3.1267856538.1614760741; _gid=GA1.3.1052156997.1628838431; _gat=1',
        'Host': 'www.tpex.org.tw',
        'Origin': 'https://www.tpex.org.tw',
        'Referer': 'https://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php?l=zh-tw',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    }

    max_pages = 100
    page_check = True
    i = 1
    cols = []
    datas = []
    while i <= max_pages:
        payload = {'stk_code': ticker, 'charset':'UTF-8', 'g-recaptcha-response':token, 'topage':str(i)}
        res = rs.post(url, payload, headers = headers)
        page_soup = bs(res.content.decode(), 'lxml')
        # print(page_soup)
        tables = page_soup.find_all('table', {"class":"table table-striped table-bordered"})
        
        for table in tables[1:]:
            for j, tr in enumerate(table.find_all('tr')):
                if not j:
                    if not cols:
                        cols = [td.text.strip() for td in tr.find_all('td')[1:]]
                    continue
                rows = [td.text.strip().replace(u'\xa0', u'') for td in tr.find_all('td')]
                datas.append(dict((col, value) for col, value in zip(cols, rows[1:])))

        pages = page_soup.find_all('a', {'class':'table-text-over'})
        if page_check:
            # print(tables[0])
            if pages:
                max_pages = int(pages[-1].text.strip())
                page_check = False
            else:
                break
        i += 1
        sleep(5)
    df = DataFrame(datas)
    if not df.empty:
        df['買進股數'] = df['買進股數'].str.replace(",",'').astype(int)
        df['賣出股數'] = df['賣出股數'].str.replace(",",'').astype(int)
        df['價格'] = df['價格'].str.replace(",",'').astype(float)
        df.to_csv(os.path.join(output_path, f'{ticker}_raw.csv'), index=False, encoding='utf-8-sig')

    # df['BrokerId'] = df['券商'].apply(lambda x: x[:4])
    # df['買進股數'] = df['買進股數'].str.replace(",",'').astype(int)
    # df['賣出股數'] = df['賣出股數'].str.replace(",",'').astype(int)
    # df['價格'] = df['價格'].str.replace(",",'').astype(float)
    # df['買進金額'] = df['價格'] * df['買進股數']
    # df['賣出金額'] = df['價格'] * df['賣出股數']
    
    # return df

def TransferData(cols, row):
    data = {}
    for k, v in zip(cols, row.split('","')[1:]):
        v = v.replace('"','').replace(',','')
        if k in '買進股數,賣出股數':
            data[k] = int(v)
        elif k in '價格':
            data[k] = float(v)
        else:
            data[k] = v
    data['BrokerId'] = data['券商'].split(' ')[0]
    data['買進金額'] = data['價格'] * data['買進股數']
    data['賣出金額'] = data['價格'] * data['賣出股數']
    return data

def GetDataCSV(rs, ticker='3105', output_path=parent, update_header=False, repeated=0, proxies={}):
    
    token = GetToken(rs)

    url = 'https://www.tpex.org.tw/web/stock/aftertrading/broker_trading/download_ALLCSV.php'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        'Content-Length': '27',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.tpex.org.tw',
        'Origin': 'https://www.tpex.org.tw',
        'Referer': 'https://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php?l=zh-tw',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }
    # if update_header:
    #     headers['Cookie'] = random.choice(Cookies)
    #     if repeated >= 5:
    #         headers['Cookie'] += '; _gat=1'
        
    pay_load = {
        'stk_code': ticker,
        'charset': 'UTF-8', 
        'g-recaptcha-response':token,
    }

    res = rs.post(url, pay_load, headers = headers)#, proxies={'http':'http:'+random.choice(list(proxies))})
    # print(res.text)
    # print(res.text)
    if  '券商買賣證券日報表查詢系統' in res.text:
        sleep(5)
        repeated += 1
        if repeated >= 15:
            os._exit(0)
        return GetDataCSV(rs, ticker, output_path, repeated >= 3, repeated=repeated, proxies=proxies)
    rows = res.text.split('\r\n')
    if len(rows[3].replace(' ','')) <= 0: 
        with open(os.path.join(output_path, f'{ticker}_raw.csv'), 'w') as f:
            f.write(','.join(rows))
        return
    
    cols = rows[2].split(',,')[0].split(',')[1:]
    datas = []
    for row in rows[3:]:
        row_odd = row_even = []
        tmp_row = row.split(',,')
        if len(tmp_row) > 1:
            row_odd, row_even = tmp_row
        else:
            row_odd = tmp_row[0]
        if row_odd:
            datas.append(TransferData(cols, row_odd))
        if row_even:
            datas.append(TransferData(cols, row_even))
    df = DataFrame(datas) # Detail
    df.to_csv(os.path.join(output_path, f'{ticker}_raw.csv'), index=False, encoding='utf-8-sig')
    # grouped_df = df.groupby('BrokerId')
    # groups = grouped_df.groups
    # summary = []
    # for group in groups:
    #     tmp_df = grouped_df.get_group(group).reset_index()
    #     del tmp_df['index']
    #     tmp_buy_df = tmp_df[tmp_df['買進股數']>=100000]
    #     tmp_sell_df = tmp_df[tmp_df['賣出股數']>=100000]

    #     total_sell_volume = tmp_sell_df['賣出股數'].sum()
    #     total_buy_volume = tmp_buy_df['買進股數'].sum()
    #     total_sell_shares = int(total_sell_volume / 1000)
    #     total_buy_shares = int(total_buy_volume / 1000)
    #     total_buy_dollar = int(tmp_buy_df['買進金額'].sum())
    #     total_sell_dollar = int(tmp_sell_df['賣出金額'].sum())
    #     avg_sell_price = tmp_sell_df['賣出金額'].sum() / total_sell_volume if total_sell_volume else 0
    #     avg_buy_price = tmp_buy_df['買進金額'].sum() / total_buy_volume if total_buy_volume else 0
    #     brokerId = tmp_df.loc[0, '券商']
    #     summary.append({
    #         '券商' : brokerId,
    #         '買進均價' : round(avg_buy_price, 2), 
    #         '賣出均價' : round(avg_sell_price, 2),
    #         '買進張數' : total_buy_shares, 
    #         '賣出張數' : total_sell_shares,
    #         '買進金額' : total_buy_dollar, 
    #         '賣出金額' : total_sell_dollar
    #     })
    # DataFrame(summary).to_csv(os.path.join(output_path, f'{ticker}_summary.csv'), index=False, encoding='utf-8-sig')
    # return {
    #     'Ticker' : ticker,
    #     'Summary':summary,
    #     'Detail':datas # list(df.T.to_dict().values())
    # }
    
def requestStockList(mode):
    url = f'https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}' # 上市:2, 上櫃:4
    response = requests.get(url)
    soup = bs(response.text, 'lxml')
    updateDate = soup.select('table')[0].select('h2')[1].text.split(':')[1].strip().replace('/', '-')
    asset_type = ''
    full_data = []
    for tr in soup.select('table')[1].select('tr')[1:]:
        if len(tr) <= 1:
            asset_type = tr.text.strip()
            continue
        full_data.append(parseData([tr, updateDate, asset_type]))
    return full_data

def parseData(args):
    tr, updateDate, asset_type = args
    tds = [x.text.strip() for x in tr]
    return {
        'Ticker':tds[0].split('\u3000')[0].strip(),
        'Name':tds[0].split('\u3000')[1].strip(),
        'ISINCode':tds[1],
        'IssueDate':tds[2].replace('/', '-'),
        'Market':tds[3],
        'Industry':tds[4],
        'CFICode':tds[5],
        'UpdateDate':updateDate,
        'AssetType':asset_type
    }
    
def updateOutput(args):
    """update output"""
    res, df = args
    try:
        res.update({'_id':df[df.Ticker==res['Ticker']]['_id'].values[0]})
    except:
        pass
    return res
    
if __name__ == '__main__':
    tickers = [x['Ticker'] for x in requestStockList(4) if x['AssetType'] in ['股票', "臺灣存託憑證"]]
    tdStr = datetime.today().strftime("%Y%m%d")
    # tdStr = datetime(2021,8,14).strftime("%Y%m%d")
    output_path = os.path.join(parent, 'broker_history', tdStr)
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    rs = requests.Session()
    proxies = get_proxies()
    tickers = '8255,6683,6568,6462,6419,6411,6223,6104,5351,5210,4721,3675,3552,3527,3363,2641'.split(',')
    for ticker in tickers:
        if not os.path.isfile(os.path.join(output_path, f'{ticker}_raw.csv')):
            print(ticker)
            try:
                # data = GetDataCSV(rs, ticker, output_path, proxies=proxies)
                data = GetDataCSV(rs, ticker)#, output_path, proxies=proxies)
                sleep(5)
            except Exception as e:
                print(e)
                sleep(30)
                try:
                    # data = GetDataCSV(rs, ticker, output_path, proxies=proxies)
                    data = GetDataCSV(rs, ticker)#, output_path, proxies=proxies)
                    sleep(10)
                except:
                    sleep(30)
        
    os._exit(0)
    