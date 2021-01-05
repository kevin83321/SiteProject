__updated__ = '2021-01-04 21:16:52'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, createRecommandTable, Amplitude, os, 
    crawlHotStocks,
)
            
def main(min_price=40, max_price=99, num_shares=10000, shares_ratio=0):
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
        
        # volume filter and price filter
        tickers = df.Ticker.unique()
        df.Volume = df.Volume.astype(float)
        df['DealValue'] = df.Close * df.Volume
        df.Volume /= 1000
        DealValueSelect = df[df.DealValue>=2e8].Ticker.to_list()
        hotTickers = crawlHotStocks()
        VolumeSelect = VolumeFilter(df, DealValueSelect, num_shares, shares_ratio)
        AmpSelect = Amplitude(df[df.Ticker.isin(list(VolumeSelect))])
        selection = list(PriceFilter(df, list(AmpSelect), max_price, min_price))
        selection = list(set(selection).intersection(hotTickers))
        
        pre_3y = td + timedelta(-365*3)
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
                temp_df = Calc.MACD(temp_df)
                temp_df = Calc.MA(temp_df, [5,10,20,60,300])
                temp_df = Calc.EMA(temp_df, [67, 23])
                temp_df['Vol5MA'] = temp_df.Volume.rolling(5).mean()
                temp_df['Vol67MA'] = temp_df.Volume.rolling(67).mean()
                
                last_data = temp_df.loc[td.strftime('%Y-%m-%d')]
                
                # temp_df['OSC_Trend'] = temp_df['OSC'] > temp_df['OSC'].shift(1)
                # if all(temp_df['OSC_Trend'][-3:]) and all(temp_df['OSC'][-3:] > 0):
                # final_select.append(ticker)
                
                    # if temp_df.Close[-1] > temp_df.Open[-1]:
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
        
        expand_text = 'Logic by 陳信宏'
        saveRecommand(selection, 'DayTradeByChenHsinHung')
        sendResultTable(td, selection, momentums, '5', expand_text)
    except:
        print(GetException())
        
    
    
if __name__ == '__main__':
    main(min_price=40, max_price=99, num_shares=10000, shares_ratio=0)
    
    