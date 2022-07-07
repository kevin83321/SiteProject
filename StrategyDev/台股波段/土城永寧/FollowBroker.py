import requests
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime, timedelta
from pandas import DataFrame, concat, date_range, ExcelWriter
import os
from numpy import isnan
import time
import json

from utils import getSchema
from DoMail import send_mail

import warnings
warnings.filterwarnings("ignore")

parent = os.path.dirname(os.path.abspath("__file__"))
output_path = os.path.join(parent, "FollowBroker")
if not os.path.isdir(output_path):
    os.makedirs(output_path)

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
    return data

def ParseSymbol(jsStr):
    try:
        # parse symbol
        tmp_symbol, tmp_name = str(jsStr).split(',')
        symbol_p = re.compile("GenLink2stk\(*")
        symbol_p.search(tmp_symbol)
        symbol = symbol_p.split(tmp_symbol)[1].replace("\'","").replace("AS","")
        # parse name
        name = tmp_name.split(")")[0].replace("\'", "")
        return symbol + " " + name
    except:
        raw_name = jsStr.text.strip()
        tmp_symbol, tmp_name = str(jsStr).split(';')
        symbol_p = re.compile("Link2Stk\(*")
        symbol_p.search(tmp_symbol)
        symbol = symbol_p.split(tmp_symbol)[1][:-1].replace("\'", "")
        name = raw_name.replace(symbol, "")
        return symbol + " " + name
    
def ParseHtml(table, table_type="E"):
    cols = []
    datas = []
    for i, tr in enumerate(table.find_all('tr')):
        if not i: continue
        if i == 1:
            cols = [td.text.strip() for td in tr.find_all('td')]
            cols[0] = "代碼名稱"
            cols[-1] += "(張數)" if table_type == "E" else "(金額)"
            continue
        else:
            tds = [td.text.strip() for td in tr.find_all('td')]
            if "無此券商分點交易資料" in tds: return None
            tds[0] = ParseSymbol(tr.find_all('td', {'id':'oAddCheckbox'})[0])
            datas.append(dict((col, value) for col, value in zip(cols, tds)))
    return datas

def GetBrokerTable(broker_id,branch_id, date=datetime.today(), table_type="E"):
    dateStr = date.strftime("%Y-%m-%d")
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Host": "jsjustweb.jihsun.com.tw",
        # Referer: http://jsjustweb.jihsun.com.tw/z/zg/zgb/zgb0.djhtm?a=9200&b=9217&c=B&e=2021-7-14&f=2021-7-14
        'Upgrade-Insecure-Requests': "1",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    }

    url = f'http://jsjustweb.jihsun.com.tw/z/zg/zgb/zgb0.djhtm?a={broker_id}&b={branch_id}&c={table_type}&e={dateStr}&f={dateStr}'
#     url_KShares = 'http://jsjustweb.jihsun.com.tw/z/zg/zgb/zgb0.djhtm?a=9200&b=9217&c=E&e=2021-7-21&f=2021-7-21'
#     url_dollar = 'http://jsjustweb.jihsun.com.tw/z/zg/zgb/zgb0.djhtm?a=9200&b=9217&c=B&e=2021-7-14&f=2021-7-14'
    print(url)
    js = requests.get(url, headers=headers)

    soup = bs(js.text, 'lxml')

    return soup.find_all('table', {"class":"t0"})

def ConbineData(over_Sell_data_Share, over_Buy_data_Share, over_Sell_data_Dollar, over_Buy_data_Dollar,
               today_up_limit_tickers=None, last_up_limit_tickers=None):
    
    over_buy_df = CombineBuyData(over_Buy_data_Share, over_Buy_data_Dollar)
    over_Sell_df = CombineSellData(over_Sell_data_Dollar, over_Sell_data_Share)
    return over_buy_df, over_Sell_df

def CombineBuyData(over_Buy_data_Share, over_Buy_data_Dollar):
    over_buy_df = DataFrame()
    try:
        over_Buy_df_Share = DataFrame(over_Buy_data_Share)
        over_Buy_df_Share["Ticker"] = over_Buy_df_Share["代碼名稱"].apply(lambda x: x.split(' ')[0])
        over_Buy_df_Share = over_Buy_df_Share.set_index(["代碼名稱", 'Ticker'])

        over_Buy_df_Dollar = DataFrame(over_Buy_data_Dollar)
        over_Buy_df_Dollar["Ticker"] = over_Buy_df_Dollar["代碼名稱"].apply(lambda x: x.split(' ')[0])
        over_Buy_df_Dollar = over_Buy_df_Dollar.set_index(["代碼名稱", 'Ticker'])
        over_buy_df = concat([over_Buy_df_Share, over_Buy_df_Dollar], axis=1)
    except:
        pass
    return over_buy_df

def CombineSellData(over_Sell_data_Dollar, over_Sell_data_Share):
    over_Sell_df = DataFrame()
    try:
        over_Sell_df_Share = DataFrame(over_Sell_data_Share)
        over_Sell_df_Share["Ticker"] = over_Sell_df_Share["代碼名稱"].apply(lambda x: x.split(' ')[0])
        over_Sell_df_Share = over_Sell_df_Share.set_index(["代碼名稱", 'Ticker'])

        over_Sell_df_Dollar = DataFrame(over_Sell_data_Dollar)
        over_Sell_df_Dollar["Ticker"] = over_Sell_df_Dollar["代碼名稱"].apply(lambda x: x.split(' ')[0])
        over_Sell_df_Dollar = over_Sell_df_Dollar.set_index(["代碼名稱", 'Ticker'])
        over_Sell_df = concat([over_Sell_df_Share, over_Sell_df_Dollar], axis=1)
    except:
        pass
    return over_Sell_df

# date = datetime.today()
def GetData(date = datetime.today()):
    
    # date = datetime(2021,7,21)
    dateStr = date.strftime("%Y%m%d")
    # output_path = os.path.join(parent, "Output", dateStr)
    # if not os.path.isdir(output_path):
    #     os.makedirs(output_path)
    for broker, branchs in indeed_broker.items():
        for branch in branchs:
            print(broker, branch)
            tmp_broker = brokers[broker]
            broker_id = tmp_broker['broker_id']
            branch_id = tmp_broker[broker+'-'+branch]
            #---------------------
            # Today Data
            #---------------------
            Share_tables = GetBrokerTable(broker_id, branch_id, date)
            Dollar_tables = GetBrokerTable(broker_id, branch_id, date, table_type = "B")

            # Share Table Parse
            over_Sell_data_Share = ParseHtml(Share_tables[1])
            over_Buy_data_Share = ParseHtml(Share_tables[0])

            # Dollar Table Parse
            over_Sell_data_Dollar = ParseHtml(Dollar_tables[1], "B")
            over_Buy_data_Dollar = ParseHtml(Dollar_tables[0], "B")
            over_buy_df = DataFrame()
            over_sell_df = DataFrame()
            # print(over_Sell_data_Share, '\n\n', over_Buy_data_Share, '\n\n', over_Sell_data_Dollar, '\n\n', over_Buy_data_Dollar)
            
            if any([over_Sell_data_Share, over_Buy_data_Share, over_Sell_data_Dollar, over_Buy_data_Dollar]):
                over_buy_df, over_sell_df = ConbineData(over_Sell_data_Share, over_Buy_data_Share, 
                                                        over_Sell_data_Dollar, over_Buy_data_Dollar)

                # tmp_over_sell_df = over_sell_df.dropna()#[over_sell_df.index.isin(yes_over_buy_df.index)].dropna()

                # tmp_over_sell_df['賣出均價'] = tmp_over_sell_df['賣出金額'].apply(lambda x: abs(int(str(x).replace(",", "")))) / tmp_over_sell_df['賣出張數'].apply(lambda x: abs(int(str(x).replace(",", ""))))
                # over_sell_df = concat([over_sell_df, tmp_over_sell_df[['賣出均價']]], axis=1)
            else:
                print(f'No Data {dateStr}')
    return over_buy_df.reset_index(), over_sell_df.reset_index()

def main(date = datetime.today()):
    if date.isocalendar()[-1] > 5: return
    files = [os.path.join(output_path, f"{date.strftime('%Y%m%d')}_OverSell.csv"), os.path.join(output_path, f"{date.strftime('%Y%m%d')}_OverBuy.csv")]
    files = [x for x in files if os.path.isfile(x)]
    if len(files): return
    ob_df, os_df = GetData(date)
    # print(ob_df)
    # print(os_df)
    try:
        ob_df = ob_df[ob_df['差額(張數)'].apply(lambda x: float(str(x).replace(',',''))) >= 100]
        ob_df['買入均價'] = ob_df['差額(金額)'].apply(lambda x: float(str(x).replace(',',''))) / ob_df['差額(張數)'].apply(lambda x: float(str(x).replace(',','')))
        ob_df['買入均價'] = ob_df['買入均價'].apply(lambda x: round(x, 2))
        ob_df['名稱'] = ob_df['代碼名稱'].apply(lambda x: x.split(' ')[-1])
        ob_df = ob_df['名稱,Ticker,差額(張數),差額(金額),買入均價'.split(",")]
        h_data = StockInterDay(date, date, ",".join(list(ob_df.Ticker)))
        h_df = DataFrame(h_data)
        ob_df = concat([ob_df.set_index('Ticker'), h_df.set_index("Ticker")[['Volume']]], axis=1)
        ob_df['成交量'] = ob_df.Volume.apply(lambda x: int(float(str(x).replace(',',''))/1000))
        ob_df['買入占比'] = (ob_df['差額(張數)'].apply(lambda x: float(str(x).replace(',',''))) / ob_df['成交量']).apply(lambda x: round(x*100, 2))
        del ob_df['Volume']
        ob_df.index = "\'" + ob_df.index
        ob_df.to_csv(os.path.join(output_path, f"{date.strftime('%Y%m%d')}_OverBuy.csv"), encoding='utf-8-sig')
        time.sleep(1)
    except Exception as e:
        print(date, 'OverBuy', e)

    try:
        os_df = os_df[os_df['差額(張數)'].apply(lambda x: abs(float(str(x).replace(',','')))) >= 100].dropna()
        os_df['賣出均價'] = os_df['差額(金額)'].apply(lambda x: float(str(x).replace(',',''))) / os_df['差額(張數)'].apply(lambda x: float(str(x).replace(',','')))
        os_df['賣出均價'] = os_df['賣出均價'].apply(lambda x: round(x, 2))
        os_df['名稱'] = os_df['代碼名稱'].apply(lambda x: x.split(' ')[-1])
        os_df = os_df['名稱,Ticker,差額(張數),差額(金額),賣出均價'.split(",")]
        h_data = StockInterDay(date, date, ",".join(list(os_df.Ticker)))
        h_df = DataFrame(h_data)
        os_df = concat([os_df.set_index('Ticker'), h_df.set_index("Ticker")[['Volume']]], axis=1)
        os_df['成交量'] = os_df.Volume.apply(lambda x: int(float(str(x).replace(',',''))/1000))
        os_df['賣出占比'] = (os_df['差額(張數)'].apply(lambda x: abs(float(str(x).replace(',','')))) / os_df['成交量']).apply(lambda x: round(x*100, 2))
        del os_df['Volume']
        os_df.index = "\'" + os_df.index
        os_df.to_csv(os.path.join(output_path, f"{date.strftime('%Y%m%d')}_OverSell.csv"), encoding='utf-8-sig')
        time.sleep(1)
    except Exception as e:
        print(date, 'OverSell', e)

    files = [os.path.join(output_path, f"{date.strftime('%Y%m%d')}_OverSell.csv"), os.path.join(output_path, f"{date.strftime('%Y%m%d')}_OverBuy.csv")]
    files = [x for x in files if os.path.isfile(x)]
    if files:
        mail_title = '土城小跟班'
        mail_msg = "如主旨\n\n"
        mail_msg += "最喜歡跟在土城老哥後面撿錢了\n"
        mail_msg += "此信件由 '無腦秘書' 寄送請勿回覆\n"
        send_mail('kevin83321@gmail.com', 'yqawneecqdwaluwt', ['akyang0830@outlook.com'], mail_title, mail_msg, files, cc=['kevin83321@gmail.com'])
        
    
if __name__ == '__main__':
    indeed_broker ={
        '元大':['土城永寧'],  # ,'竹科'
    #     '日盛':['文化'],
    #     '永豐金':['松山'],
    #     '凱基':['大直','松山','市政','信義'],
    #     '富邦':['建國','員林'],
    #     '群益金鼎':['大安']
    }
    with open(os.path.join(parent, 'jihsun_Broker_id_map.json'), 'r') as f:
        brokers= json.load(f)
    main()
    # main(date = datetime(2022,7,4))
    os._exit(0)