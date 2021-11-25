__updated__ = '2021-10-24 10:02:18'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, createRecommandTable
)
            
def main(min_price=15, max_price=100, num_shares=1000, shares_ratio=1):
    try:
        # setup date
        td, last = getDateBeforeTrade()
        print(td, last)
        
        # setup data
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
        selection = list(VolumeSelect)
        # selection = list(PriceFilter(df, list(VolumeSelect), max_price, min_price))

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

                temp_df = Calc.BBAND(temp_df, 20, 2)
                if temp_df is None or temp_df.empty:continue
                temp_df = Calc.MA(temp_df, [5,10])
                if temp_df is None or temp_df.empty:continue
                temp_df['bandwpct_chg'] = temp_df.bandwidth.pct_change()
                temp_df['bandwpct_chg_std'] = temp_df['bandwpct_chg'].rolling(20).std()

                temp_df['slope20'] = temp_df.MA20.pct_change()
                temp_df['slope5'] = temp_df.MA5.pct_change()
                temp_df['slope10'] = temp_df.MA10.pct_change()

                condi1 = temp_df.slope5.iloc[-1] < 0
                condi2 = temp_df.slope10.iloc[-1] < 0
                condi3 = temp_df.slope20.iloc[-1] < 0
                condi4 = temp_df.bandwpct_chg.pct_change().iloc[-1] > 0
                condi6 = temp_df['bandwpct_chg_std'].pct_change().iloc[-1] > 0
                condi5 = temp_df.MA5.iloc[-1] < temp_df.MA10.iloc[-1]  and temp_df.MA10.iloc[-1] < temp_df.MA20.iloc[-1] 
                # condi7 = temp_df['bandwidth'].iloc[-1] >= 0.1
                if all([condi1,condi2,condi3,condi4,condi5, condi6]):
                    mom = Calc.Momemtum(temp_df)
                    if mom is None:continue
                    final_select.append(ticker)
                    momentums.append((ticker, mom))
            except:
                pass
        
        saveRecommand(final_select, 'WeakTrend')
        expand_text = "弱勢股挑選 : 開布林，MA(5,20)趨勢向下，布林變動加大\n"
        expand_text += "這是一個放空選股，請不要傻傻做多當韭菜\n"
        expand_text += "進場 : 隔日K棒過布林過窄不進(上通道/下通道-1)\n"
        expand_text += "出場 : 損 : 10%, 在布林底部反轉出現紅K向上穿越MA5(最低價>MA5)"
        sendResultTable(td, final_select, momentums, '9', expand_text=expand_text)
        
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
    main(min_price=15, max_price=100, num_shares=1000, shares_ratio=1)
    
    