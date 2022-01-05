__updated__ = '2021-12-24 00:57:01'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, createRecommandTable, datetime
)

def ReadSTCFUTMapping():
    # ===============
    # 讀取新檔案
    # ===============
    url = 'https://www.taifex.com.tw/file/taifex/CHINESE/2/2_stockinfo.ods'
    stc_fut_df = pd.read_excel(url, skiprows=2, dtype=str, engine='odf')[:-2]
    stc_fut_df.columns = 'FUT_Ticker,FullName,STC_Ticker,ShortName,HasFut,HasOpt,List,OTC,ListETF,Multiplier'.split(',')
    stc_fut_df.loc[stc_fut_df[stc_fut_df.FUT_Ticker.isna()].index,"FUT_Ticker"] = "NA"
    datas = []
    
    mapping = {'TickerToName':{}, 'Multiplier':{}, 'FutToStc':{}, 'NameToTicker':{}, 'NameToTickerFut':{}, 'Fee':{}}
    
    for row in stc_fut_df.itertuples():
        
        # update stock
        STC_Ticker = ("00"+row.STC_Ticker if not row.STC_Ticker.startswith('0') else row.STC_Ticker) if "ETF" in row.ShortName.strip() else row.STC_Ticker
        mapping['NameToTicker'].update({row.ShortName.strip(): STC_Ticker})
        mapping['NameToTicker'].update({row.ShortName.strip().replace("ETF", ""): STC_Ticker})
        mapping['TickerToName'].update({STC_Ticker: row.ShortName.strip()})
        mapping['Multiplier'][STC_Ticker] = 1000
        # mapping['Fee'][STC_Ticker] = 3e-3
        # update future
        
        mapping['Fee'][row.FUT_Ticker] = 2e-5
        if int(row.Multiplier) == 100:
            mapping['NameToTickerFut'].update({'小'+row.ShortName+'期貨': row.FUT_Ticker})
            mapping['NameToTickerFut'].update({'小'+row.ShortName+'期': row.FUT_Ticker})
        else:
            mapping['NameToTickerFut'].update({row.ShortName+'期貨': row.FUT_Ticker})
            mapping['NameToTickerFut'].update({row.ShortName+'期': row.FUT_Ticker})
        if int(row.Multiplier) == 10000:
            mapping['NameToTickerFut'].update({row.ShortName.strip().replace('ETF', '期貨'): row.FUT_Ticker})
            mapping['NameToTickerFut'].update({row.ShortName.strip().replace('ETF', ''): row.FUT_Ticker})
            mapping['NameToTickerFut'].update({row.ShortName.strip(): row.FUT_Ticker})
            # mapping['Fee'][STC_Ticker] = 1e-3
        # 元大上證50ETF期
        
        mapping['Multiplier'][row.FUT_Ticker[:2]] = int(row.Multiplier)
        mapping['FutToStc'].update({row.FUT_Ticker: STC_Ticker})
    return mapping
            
def main(date=datetime.today(), min_price=15, max_price=100, num_shares=1000, shares_ratio=1):
    try:
        fut_stc_mapping = ReadSTCFUTMapping()
        # setup date
        td, last = getDateBeforeTrade(date)
        # print(td, last)
        
        # setup data
        schema = getSchema('TWSE')
        table = schema['StockList']
        last_date = sorted(table.distinct("UpdateDate"))[-1]
        info_data = dict((x['Ticker'], x['Industry']+f"({x['Market'][-1]})") for x in table.find({"UpdateDate":{"$eq":last_date}}))
        
        schema = getSchema('TWSE')
        table = schema['historicalPrice']
        data = list(table.find({'Date':{'$gte':last.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
        
        if data:
            df = pd.DataFrame(data).set_index('Date')
        else:
            data = list(table.find({'Date':{'$gte':(last+timedelta(-30)).strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
            df = pd.DataFrame(data).set_index('Date')
            df = df.loc[sorted(df.index.unique())[-2:], :]
        if len(df.index.unique()) < 2:
            data = list(table.find({'Date':{'$gte':(last+timedelta(-30)).strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
            df = pd.DataFrame(data).set_index('Date')
            df = df.loc[sorted(df.index.unique())[-2:], :]
        del df['_id']
        for col in 'Open,High,Low,Close,Volume'.split(','):
            df[col] = df[col].apply(changedType)

        tickers = df.Ticker.unique()
        df.Volume = df.Volume.astype(float)
        df.Volume /= 1000
        VolumeSelect = VolumeFilter(df, tickers, num_shares, shares_ratio)
        # selection = list(VolumeSelect)
        selection = list(PriceFilter(df, list(VolumeSelect), max_price, min_price))

        final_select = []
        momentums = []
        for ticker in selection: # tickers:#
            try:
                pre_3y = td + timedelta(-365*1)
                temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))).set_index('Date')
                
                if temp_df is None or temp_df.empty:continue
                del temp_df['_id']
                temp_df.Close = temp_df.Close.replace('--', float('nan'))
                temp_df.High = temp_df.High.replace('--', float('nan'))
                temp_df.Low = temp_df.Low.replace('--', float('nan'))
                temp_df.Open = temp_df.Open.replace('--', float('nan'))
                if temp_df is None:
                    print(ticker, 'is None', temp_df)
                    continue
                if temp_df.empty:
                    print(ticker, 'is empty', temp_df)
                    continue
                for col in 'Open,High,Low,Close,Volume'.split(','):
                    temp_df[col] = temp_df[col].apply(changedType)

                max_oc = temp_df[['Close', 'Open']].max(axis=1)
                min_oc = temp_df[['Close', 'Open']].min(axis=1)
                # last_two_max = max(temp_df.Close.iloc[-3], temp_df.Open.iloc[-3])
                # last_one_max = max(temp_df.Close.iloc[-2], temp_df.Open.iloc[-2])
                # td_max = max(temp_df.Close.iloc[-1], temp_df.Open)
                # temp_df = Calc.BBAND(temp_df, 20, 2)
                # if temp_df is None or temp_df.empty:continue
                # temp_df = Calc.MA(temp_df, [5,10, 20])
                # if temp_df is None or temp_df.empty:continue
                # temp_df['bandwpct_chg'] = temp_df.bandwidth.pct_change()
                # temp_df['bandwpct_chg_std'] = temp_df['bandwpct_chg'].rolling(20).std()

                # temp_df['slope20'] = temp_df.MA20.pct_change()
                # temp_df['slope5'] = temp_df.MA5.pct_change()
                # temp_df['slope10'] = temp_df.MA10.pct_change()
                # temp_df['Ret'] = temp_df.Close.pct_change()

                condi1 = temp_df.Close.iloc[-3] > temp_df.Open.iloc[-3]
                condi2 = max(max_oc.iloc[-3], max_oc.iloc[-1]) < min_oc.iloc[-2]
                # condi3 = min_oc.iloc[-2] > max_oc.iloc[-1]
                condi4 = (temp_df.Volume.iloc[-1] / temp_df.Volume.iloc[-2]) > shares_ratio
                condi5 = temp_df.Close.iloc[-1] < min(temp_df.Open.iloc[-1], max_oc.iloc[-3])
                # condi1 = max(max_oc.iloc[-3], max_oc.iloc[-1]) < max_oc.iloc[-2] # temp_df.slope5.pct_change().iloc[-1] < 0#
                # condi2 = (max_oc.iloc[-2] / max_oc.iloc[-22] - 1) >= .2
                # condi3 = temp_df.Low.iloc[-1] <= temp_df.MA10.iloc[-1]
                # condi4 = temp_df.slope10.pct_change().iloc[-1] < 0
                # condi5 = temp_df.High.iloc[-2] > temp_df.MA20.iloc[-2] and temp_df.Low.iloc[-2] < temp_df.MA20.iloc[-2]
                # condi2 = temp_df.Close.iloc[-1] < min(temp_df.Open.iloc[-1], temp_df.MA20.iloc[-1])#, temp_df.Low.iloc[-2])
                # condi3 = ticker in fut_stc_mapping['TickerToName'].keys() or True
                # condi6 = #temp_df['Ret'].iloc[-1] < 0
                # condi4 = temp_df.bandwpct_chg.pct_change().iloc[-1] > 0
                # condi6 = temp_df['bandwpct_chg_std'].pct_change().iloc[-1] > 0
                # condi5 = temp_df.MA5.iloc[-1] < temp_df.MA10.iloc[-1]  and temp_df.MA10.iloc[-1] < temp_df.MA20.iloc[-1] 
                # condi7 = temp_df['bandwidth'].iloc[-1] >= 0.1
                if all([condi1, condi2, condi4, condi5]): # ,condi3,condi4,condi5, condi6 
                    mom = Calc.Momemtum(temp_df)
                    if mom is None:continue
                    final_select.append(ticker)
                    momentums.append((ticker, mom))
            except Exception as e:
                pass
                # print(e)
                # os._exit(0)
        
        saveRecommand(final_select, 'WeakTrend')
        expand_text = "弱勢股挑選 : 頭部A轉，近一日收黑K\n" #(波段漲幅>20%)
        expand_text += "這是一個放空選股，請不要傻傻做多當韭菜\n"
        expand_text += "進場 : 隔日K棒接近收盤時為黑K或常上引線紅K\n"
        # expand_text += "出場 : 損 : 10%, 在布林底部反轉出現紅K向上穿越MA5(最低價>MA5)"
        sendResultTable(td, final_select, momentums, '9', expand_text=expand_text, Industry=info_data)
        
        # saveRecommand(select_by_EMA67_23, 'VolumeWithMACD_EMA67_23')
        # sendResultTable(td, select_by_EMA67_23, momentums, '1-1')
        
        # saveRecommand(select_by_Volume5, 'VolumeWithMACD_EMA67_23_VOL5')
        # sendResultTable(td, select_by_Volume5, momentums, '1-2')
        
        # saveRecommand(select_by_Volume67, 'VolumeWithMACD_EMA67_23_VOL67')
        # sendResultTable(td, select_by_Volume67, momentums, '1-3')
        
        # select_by_Volume5_67 = list(set(select_by_Volume5).intersection(select_by_Volume67))
        # saveRecommand(select_by_Volume5_67, 'VolumeWithMACD_EMA67_23_VOL5_67')
        # sendResultTable(td, select_by_Volume5_67, momentums, '1-4')
    except:
        print(GetException())
        
    
    
if __name__ == '__main__':
    # main(date=datetime(2021,4,24), min_price=15, max_price=9999, num_shares=1000, shares_ratio=1)
    main(min_price=15, max_price=9999, num_shares=1000, shares_ratio=1)
    
    