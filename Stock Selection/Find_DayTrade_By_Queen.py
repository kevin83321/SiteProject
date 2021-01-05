

__updated__ = '2021-01-04 21:16:42'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, createRecommandTable,
    Increase, os, #totalValue,
    # Increase_filter, Decrease_filter,
    getStockList, parseRollingData
)
            
def main(num_shares=2000, shares_ratio=1.5):
    try:
        # setup date
        td, last = getDateBeforeTrade()
        
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
            
        #
        listed_tickers, otc_tickers = getStockList(schema)
        # do filter listed
        df_listed = df[df.Ticker.isin(listed_tickers)]
        increase_tickers = list(Increase(df_listed, listed_tickers))

        # do filter otc
        df_otc = df[df.Ticker.isin(otc_tickers)]
        increase_tickers_otc = list(Increase(df_otc, otc_tickers))
        
        # volume filter
        df.Volume = df.Volume.astype(float)
        df.Volume /= 1000
        temp_df_list = df_listed[df_listed.index == last.strftime('%Y-%m-%d')]
        temp_df_otc = df_otc[df_otc.index == last.strftime('%Y-%m-%d')]
        selection_listed = temp_df_list[(temp_df_list.Volume >= num_shares) & (temp_df_list.Ticker.isin(increase_tickers))].Ticker.unique()
        selection_otc = temp_df_otc[(temp_df_otc.Volume >= num_shares) & (temp_df_otc.Ticker.isin(increase_tickers_otc))].Ticker.unique()
        print('量能過濾')
        print('listed stocks', selection_listed)
        print('\n')
        print('otc stocks', selection_otc)
        
        
        tickers = df.Ticker.unique()
        increase_ticker_all = list(Increase(df, tickers))
        temp_df = df[df.index == last.strftime('%Y-%m-%d')]
        selection = temp_df[(temp_df.Volume >= num_shares) & (temp_df.Ticker.isin(increase_ticker_all))].Ticker.unique()
        print('\n combine', selection)
        
        # os._exit(0)
        
        
        final_select = []
        pre_3y = td + timedelta(-365*3)
        select_by_EMA67_23 = []
        select_by_Volume5 = []
        select_by_Volume67 = []
        momentums = []
        for ticker in selection:
            try:
                temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))).set_index('Date')
                if temp_df is None:
                    print(ticker, 'is None', temp_df)
                    continue
                if temp_df.empty:
                    print(ticker, 'is empty', temp_df)
                    continue
                for col in 'Open,High,Low,Close,Volume'.split(','):
                    temp_df[col] = temp_df[col].apply(changedType)
                # temp_df = parseRollingData(temp_df.copy(deep=True), 'W')
                temp_df = Calc.MACD(temp_df)
                temp_df = Calc.MA(temp_df, [4,10,20,60,300])
                # temp_df['Ret_ma'] = temp_df.MA
                temp_df = Calc.EMA(temp_df, [67, 23])
                temp_df['Vol5MA'] = temp_df.Volume.rolling(5).mean()
                temp_df['Vol67MA'] = temp_df.Volume.rolling(67).mean()
                
                last_data = temp_df.loc[td.strftime('%Y-%m-%d')] 
                
                if temp_df.Volume[-1] > max(temp_df.Vol5MA[-2], temp_df.Volume[-2]) * shares_ratio:
                    temp_df['OSC_Trend'] = temp_df['OSC'] > temp_df['OSC'].shift(1)
                    if all(temp_df['OSC_Trend'][-3:]) and all(temp_df['OSC'][-3:] > 0):
                        if temp_df.Close[-1] > max(temp_df.Close[-2], temp_df.Open[-1]):
                            final_select.append(ticker)
                    
                        # if temp_df.Close[-1] > temp_df.Open[-1] :
                        #     if temp_df.Low[-1] >= temp_df.EMA67[-1]:
                        #         if temp_df.Low[-1] >= temp_df.EMA23[-1]:
                        #             select_by_EMA67_23.append(ticker)
                                    
                        #             if temp_df.Volume[-1] > temp_df.Vol5MA[-1] * shares_ratio:
                        #                 select_by_Volume5.append(ticker)
                        #             if temp_df.Volume[-1] > temp_df.Vol67MA[-1] * shares_ratio:
                        #                 select_by_Volume67.append(ticker)
                            momentums.append((ticker, Calc.Momemtum(temp_df)))
                            # output figure
                            temp_df = temp_df.tail(200)
                            createPlot(td, temp_df, ticker, MACD=True)
            except:
                print(GetException())
        # print(f'final selection', final_select)
        # print(df[df.Ticker.isin(final_select)])
        expand_text = 'Logic by Queen\n'
        expand_text += 'Adjust with MACD And Volume > MA5 or Yesterday\n'
        saveRecommand(final_select, 'DayTrade_by_Queen')
        sendResultTable(td, final_select, momentums, '3', expand_text)
    except:
        print(GetException())
        
    
    
if __name__ == '__main__':
    main(num_shares=500, shares_ratio=2)
    
    