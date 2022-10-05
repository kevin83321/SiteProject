import requests
import os
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime, timedelta
import time

from Utils import *

from BaseObj import CallOption, PutOption
from OptionFunc import getThirdWendesday

def crawlOptDailyMarketReport(date:datetime=datetime.today(), settle=False, update=False):
    
    url = 'https://www.taifex.com.tw/cht/3/optDailyMarketReport'
    pay_load = {
        "queryType": "2",
        "marketCode": "0",
        "dateaddcnt": "",
        "commodity_id": "TXO",
        "commodity_id2": "",
        "queryDate": date.strftime("%Y/%m/%d"),
        "MarketCode": "0",
        "commodity_idt": "TXO",
        "commodity_id2t": "",
        "commodity_id2t2": ""
    }
    df = pd.DataFrame()
    f_path = os.path.join(output_path, '每日成交資訊', f'Opt_{date.strftime("%Y%m%d")}.txt')
    checkPath(os.path.dirname(f_path))
    if os.path.isfile(f_path) and not update:
        df = pd.read_csv(f_path, encoding='utf-8-sig',dtype=str)
    else:
        try:
            res = requests.post(url, data=pay_load)
            soup = bs(res.content, 'lxml')
            table = soup.find_all('table', {'class':"table_f"})[0]
            cols = [th.text.strip() for th in table.find_all('th')]
            out = []
            for tr in table.find_all('tr'):
                if '鉅額' in tr.text or '小計' in tr.text:continue
                tmp = [td.text.strip() for td in tr.find_all('td')]
                if tmp:
                    out.append(dict((k, v) for k, v in zip(cols, tmp)))
            df = pd.DataFrame(out)
            df.to_csv(f_path, index=False, encoding='utf-8-sig')
        except:
            pass
    if not df.empty:
        ttm_  = getThirdWendesday(date)
        df = df['到期月份(週別),履約價,買賣權,最後成交價,結算價,*未沖銷契約量,最後最佳買價,最後最佳賣價'.split(',')]
        df.columns = 'Maturity,Strike,CP,Close,SettlePrice,OI,BestBid,BestAsk'.split(',')
        print(ttm_.date(), date.date(), settle, ttm_.date()==date.date() or settle)
        ttm = [x for x in sorted(df.Maturity.unique()) if 'W' not in x][int(ttm_.date()==date.date() or settle)]
        df = df[df.Maturity==ttm]
    return df

def getOptDailyMarketReport(date = datetime.today(), update=False):
    date += timedelta(1)
    last_date = None
    last_df = None # 今日
    pre_df = None # 前一日
    i = -1
    while 1:
        
        tmp_date = date + timedelta(i)
        # print(tmp_date, last_date)
        if tmp_date.isocalendar()[-1] > 5:
            i -= 1
            continue
        ttm_  = getThirdWendesday(tmp_date)
        tmp = crawlOptDailyMarketReport(tmp_date, 
                                        settle=(ttm_.date()==last_date.date() if last_date else 0), update=update)
        # print(tmp)
        if last_df is None:
            if not tmp.empty:
                last_df = tmp
                if not last_date:
                    last_date = tmp_date
        elif pre_df is None:
            if not tmp.empty:
                pre_df = tmp
        if last_df is not None and pre_df is not None:
            if not last_df.empty and not pre_df.empty:
                break
        time.sleep(3)
        i -= 1
    
    last_df[list(last_df.columns)[:-5]] = last_df[list(last_df.columns)[:-5]].astype(str)
    pre_df[list(pre_df.columns)[:-5]] = pre_df[list(pre_df.columns)[:-5]].astype(str)
    last_df.columns = list(last_df.columns)[:-5] + ['Close_last', "Settle_last", 'OI_last', 'BestBid_last', 'BestAsk_last']
    pre_df.columns = list(pre_df.columns)[:-5] + ['Close_pre', "Settle_pre", 'OI_pre', 'BestBid_pre', 'BestAsk_pre']
    df = pd.concat([last_df.set_index('Maturity,Strike,CP'.split(',')), pre_df.set_index('Maturity,Strike,CP'.split(','))], axis=1)
    print(df)
    df['OI_Diff'] = df['OI_last'].astype(float) - df['OI_pre'].astype(float)
    return df, last_date

def crawlPCRatio(date:datetime = datetime.today()):
    url = "https://www.taifex.com.tw/cht/3/pcRatio"
    pay_load = {
        "down_type": "",
        "queryStartDate": date.strftime("%Y/%m/%d"), # "2022/08/18",
        "queryEndDate": date.strftime("%Y/%m/%d"), # "2022/09/17"
    }
    res = requests.post(url, data=pay_load)
    soup = bs(res.content, 'lxml')
    table = soup.find_all('table', {'class':"table_a"})[0]
    cols = [th.text.strip() for th in table.find_all('th')]
    out = []
    for tr in table.find_all('tr'):
        if '鉅額' in tr.text or '小計' in tr.text:continue
        tmp = [td.text.strip() for td in tr.find_all('td')]
        if tmp:
            out.append(dict((k, v) for k, v in zip(cols, tmp)))
    df = pd.DataFrame(out)
    return df

def crawlInstitutionTraded(date:datetime = datetime.today()):
    url = "https://www.taifex.com.tw/cht/3/callsAndPutsDate"
    pay_load = {
        "queryType": "1",
        "goDay": "",
        "doQuery": "1",
        "dateaddcnt": "",
        "queryDate": date.strftime("%Y/%m/%d"),
        "commodityId": ""
    }
    df = pd.DataFrame()
    f_path = os.path.join(output_path, '三大法人', f'Opt_{date.strftime("%Y%m%d")}.txt')
    checkPath(os.path.dirname(f_path))
    if os.path.isfile(f_path):
        df = pd.read_csv(f_path, encoding='utf-8-sig',dtype=str)
    else:
        try:
            res = requests.post(url, data=pay_load)
            soup = bs(res.content, 'lxml')
            table = soup.find_all('table', {'class':"table_f"})[0]
            cols = '序號,商品,權別,身分別,買方口數(交易),買方金額(交易),賣方口數(交易),賣方金額(交易),差額口數(交易),差額金額(交易)'.split(',')
            cols.extend('買方口數(OI),買方金額(OI),賣方口數(OI),賣方金額(OI),差額口數(OI),差額金額(OI)'.split(','))
            out = []
            for tr in table.find_all('tr')[3:]:
                if '鉅額' in tr.text or '小計' in tr.text:continue
                tmp = [td.text.strip() for td in tr.find_all('th')]+[td.text.strip() for td in tr.find_all('td')]
                if len(tmp) < len(cols):
                    tmp = last_tmp[:len(cols)-len(tmp)] + tmp
                if tmp:
                    out.append(dict((k, v) for k, v in zip(cols, tmp)))
                    last_tmp = tmp
            df = pd.DataFrame(out)
            del df['序號']
            df.to_csv(f_path, index=False, encoding='utf-8-sig')
        except:
            pass
    if not df.empty:
        df = df[df['商品']=='臺指選擇權']
        df = df['權別,身分別,差額口數(交易),差額口數(OI)'.split(',')]
    return df

def crawlLargeTraded(date:datetime = datetime.today()):

    url = "https://www.taifex.com.tw/cht/3/largeTraderOptQry"
    pay_load = {
        "datecount": "",
        "contractId2": "",
        "queryDate": date.strftime("%Y/%m/%d"),
        "contractId": "all"
    }

    df = pd.DataFrame()
    f_path = os.path.join(output_path, '大額交易人', f'Opt_{date.strftime("%Y%m%d")}.txt')
    checkPath(os.path.dirname(f_path))
    if os.path.isfile(f_path):
        df = pd.read_csv(f_path, encoding='utf-8-sig',dtype=str)
    else:
        try:
            res = requests.post(url, data=pay_load)
            soup = bs(res.content, 'lxml')
            table = soup.find_all('table', {'class':"table_f"})[0]
            cols = '契約,到期月份(週別),五大交易人(特法))買(OI),五大交易人(特法))買(Ratio),十大交易人(特法))買(OI),十大交易人(特法))買(Ratio)'.split(',')
            cols.extend("五大交易人(特法))賣(OI),五大交易人(特法))賣(Ratio),十大交易人(特法))賣(OI),十大交易人(特法))賣(Ratio),OI".split(','))
            out = []
            for tr in table.find_all('tr')[3:]:
                if '鉅額' in tr.text or '小計' in tr.text:continue
                tmp = [td.text.strip().replace('\r','').replace('\n','').replace('\t','') for td in tr.find_all('td')]
                if len(tmp) < len(cols):
                    tmp = last_tmp[:len(cols)-len(tmp)] + tmp
                if tmp:
                    out.append(dict((k, v) for k, v in zip(cols, tmp)))
                    last_tmp = tmp
            df = pd.DataFrame(out)
            del df['序號']
            df.to_csv(f_path, index=False, encoding='utf-8-sig')
        except:
            pass
    if not df.empty:
        for col in df.columns[2:]:
            df[col] = df[col].apply(lambda x: x.replace(',',''))
#         print(df)
        df = df[df['契約'].apply(lambda x: '臺指' in x)]
        df = df['契約,到期月份(週別),十大交易人(特法))買(OI),十大交易人(特法))賣(OI)'.split(',')]
    return df

def readIndexData(table, last_date):
    start_date = last_date + timedelta(-400)
    h_data = list(table.find({"Date":{"$gte":start_date.strftime("%Y-%m-%d")}, "IndexName":{"$eq":"發行量加權股價指數"}}))

    h_df = pd.DataFrame(h_data)
    del h_df['_id']

    h_df['Ret'] = np.log(h_df.Close / h_df.Close.shift(1))
    h_df['vol_20'] = h_df.Ret.rolling(20).std(ddof=1)
    h_df['vol_60'] = h_df.Ret.rolling(60).std(ddof=1)
    h_df['vol_260'] = h_df.Ret.rolling(260).std(ddof=1)
    return h_df

def readFutureData(table, last_date):
    h_f_data = list(table.find({"Date":{"$eq":last_date.strftime("%Y-%m-%d")}, "Contract":{"$eq":"TX"}}))
    df_h_f = pd.DataFrame(h_f_data)
    del df_h_f['_id']
    df_h_f = df_h_f[df_h_f.TradingSession=='Regular']
    ttm_  = getThirdWendesday(last_date)
    near_ttm = sorted([x for x in df_h_f.Maturity.unique() if '/' not in x])[int(ttm_.date()==last_date.date())]
    return df_h_f[df_h_f.Maturity==near_ttm]

def saveDailyInfo(last_date, output):
    output_ = os.path.join(output_path, "Summary", "Info")
    if not os.path.isdir(output_):
        os.makedirs(output_)
    with open(os.path.join(output_, f"{last_date.strftime('%Y-%m-%d')} Option Daily Info.json"), 'w', encoding='utf-8') as f:
        json.dump(output, f)