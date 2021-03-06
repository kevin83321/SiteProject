

__updated__ = '2020-11-26 16:54:20'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, createRecommandTable,
    Amplitude, Increase, os, totalValue,
    getStockList
)
    
def Increase_filter(df):
    value_select = list(totalValue(df))
    amp_select = list(Amplitude(df))
    inc_select = list(Increase(df,amp_select))
    return list(set(value_select).intersection(inc_select))

def Decrease_filter(df):
    value_select = list(totalValue(df))
    amp_select = list(Amplitude(df))
    dec_select = list(Increase(df, amp_select, top=False))
    return list(set(value_select).intersection(dec_select))
            
def main():
    try:
        # setup date
        td, last = getDateBeforeTrade()
        
        # setup data
        schema = getSchema('TWSE')
        table = schema['historicalPrice']
        data = list(table.find({'Date':{'$gte':last.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
        
        df = pd.DataFrame(data).set_index('Date')
        del df['_id']
        for col in 'Open,High,Low,Close,Volume'.split(','):
            df[col] = df[col].apply(changedType)
        
        
        # volume filter and price filter
        tickers = df.Ticker.unique()
        df.Volume = df.Volume.astype(float)
        df.Volume /= 1000
        
        listed_tickers, otc_tickers = getStockList(schema)
        # do filter listed
        df_listed = df[df.Ticker.isin(listed_tickers)]
        print('上市標的')
        increase_tickers = Increase_filter(df_listed)
        print('increase', increase_tickers)
        decrease_tickers = Decrease_filter(df_listed)
        print('decrease', decrease_tickers)
        
        # do filter otc
        print('上櫃標的')
        df_otc = df[df.Ticker.isin(otc_tickers)]
        increase_tickers_otc = Increase_filter(df_otc)
        print('increase', increase_tickers_otc)
        decrease_tickers_otc = Decrease_filter(df_otc)
        print('decrease', decrease_tickers_otc)
        os._exit(0)
        
        
        
        
        
        
        
        
        
        
        
        
        
        VolumeSelect = VolumeFilter(df, tickers, num_shares, shares_ratio)
        selection = list(PriceFilter(df, list(VolumeSelect), max_price, min_price))
        
        final_select = []
        pre_3y = td + timedelta(-365*3)
        select_by_EMA67_23 = []
        select_by_Volume5 = []
        select_by_Volume67 = []
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
                temp_df = Calc.MACD(temp_df)
                temp_df = Calc.MA(temp_df, [5,10,20,60,300])
                temp_df = Calc.EMA(temp_df, [67, 23])
                temp_df['Vol5MA'] = temp_df.Volume.rolling(5).mean()
                temp_df['Vol67MA'] = temp_df.Volume.rolling(67).mean()
                
                last_data = temp_df.loc[td.strftime('%Y-%m-%d')] 
                
                temp_df['OSC_Trend'] = temp_df['OSC'] > temp_df['OSC'].shift(1)
                if all(temp_df['OSC_Trend'][-3:]) and all(temp_df['OSC'][-3:] > 0):
                    final_select.append(ticker)
                
                    if temp_df.Close[-1] > temp_df.Open[-1]:
                        if temp_df.Low[-1] >= temp_df.EMA67[-1]:
                            if temp_df.Low[-1] >= temp_df.EMA23[-1]:
                                select_by_EMA67_23.append(ticker)
                                
                                if temp_df.Volume[-1] > temp_df.Vol5MA[-1] * shares_ratio:
                                    select_by_Volume5.append(ticker)
                                if temp_df.Volume[-1] > temp_df.Vol67MA[-1] * shares_ratio:
                                    select_by_Volume67.append(ticker)
                    momentums.append((ticker, Calc.Momemtum(temp_df)))
                    # output figure
                    temp_df = temp_df.tail(200)
                    createPlot(td, temp_df, ticker, MACD=True)
            except:
                print(GetException())
        
        saveRecommand(final_select, 'VolumeWithMACD')
        sendResultTable(td, final_select, momentums)
        
        saveRecommand(select_by_EMA67_23, 'VolumeWithMACD_EMA67_23')
        sendResultTable(td, select_by_EMA67_23, momentums, '1-1')
        
        saveRecommand(select_by_Volume5, 'VolumeWithMACD_EMA67_23_VOL5')
        sendResultTable(td, select_by_Volume5, momentums, '1-2')
        
        saveRecommand(select_by_Volume67, 'VolumeWithMACD_EMA67_23_VOL67')
        sendResultTable(td, select_by_Volume67, momentums, '1-3')
        
        select_by_Volume5_67 = list(set(select_by_Volume5).intersection(select_by_Volume67))
        saveRecommand(select_by_Volume5_67, 'VolumeWithMACD_EMA67_23_VOL5_67')
        sendResultTable(td, select_by_Volume5_67, momentums, '1-4')
    except:
        print(GetException())
        
    
    
if __name__ == '__main__':
    main()#min_price=20, max_price=200, num_shares=2000, shares_ratio=1.5)
    
    