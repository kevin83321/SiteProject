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
        
        df = pd.DataFrame(data).set_index('Date')
        if len(df.index.unique()) < 2:
            data = list(table.find({'Date':{'$gte':(last+timedelta(-30)).strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
            df = pd.DataFrame(data).set_index('Date')
            df = df.loc[sorted(df.index.unique())[-2:], :]
        del df['_id']
        for col in 'Open,High,Low,Close,Volume'.split(','):
            df[col] = df[col].apply(changedType)
        
        # volume filter and price filter
        tickers = df.Ticker.unique()
        df.Volume = df.Volume.astype(float)
        df.Volume /= 1000
        VolumeSelect = VolumeFilter(df, tickers, num_shares, shares_ratio)
        selection = list(PriceFilter(df, list(VolumeSelect), max_price, min_price))
        
        final_select = []
        pre_3y = td + timedelta(-365*3)
        momentums = []
        for ticker in selection:
            try:
                temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))).set_index('Date')
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
                temp_df = Calc.BBAND(temp_df, 20,2)
                temp_df = Calc.MA(temp_df, [5])
                temp_df['bandwpct_chg'] = temp_df.bandwidth.pct_change()
                temp_df['bandwpct_chg_std'] = temp_df['bandwpct_chg'].rolling(20).std()

                temp_df['slope20'] = temp_df.MA20.pct_change()
                temp_df['slope5'] = temp_df.MA5.pct_change()
                temp_df = Calc.MACD(temp_df)

                condi1 = temp_df.slope5.iloc[-1] > 0
                condi2 = temp_df.slope20.iloc[-1] > 0
                condi3 = temp_df.bandwpct_chg.pct_change().iloc[-1] > 0
                condi4 = temp_df['bandwpct_chg_std'].pct_change().iloc[-1] > 0
                condi5 = temp_df.MA5.iloc[-1] > temp_df.MA20.iloc[-1]
                condi6 = temp_df['bandwpct_chg'].iloc[-1] > 0
                condi7 = temp_df['bandwidth'].iloc[-1] <= 0.2
                if all([condi1,condi2,condi3,condi4,condi5,condi6,condi7]):
                    final_select.append(ticker)
                    momentums.append((ticker, Calc.Momemtum(temp_df)))
                    # output figure
                    temp_df = temp_df.tail(200)
                    createPlot(td, temp_df, ticker, MACD=True)
            except:
                print(GetException())
        
        saveRecommand(final_select, 'StrongTrend')
        expand_text = "強勢股挑選 : 開布林，MA(5,20)趨勢向上，布林變動加大\n"
        expand_text += "進場 : 隔日K棒過布林上緣不進，收黑K且MA20(布林中線未續上，或過布林上緣\n"
        expand_text += "出場 : 損 : 10%, 離開MA5"
        sendResultTable(td, final_select, momentums, '8', expand_text=expand_text)
        
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
    
    