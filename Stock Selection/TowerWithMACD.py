

__updated__ = '2021-01-20 21:25:09'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType
)
            
def main(min_price=0, max_price=50, num_shares=0, shares_ratio=0):
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
        df.Volume /= 1000
        selection = list(VolumeFilter(df, tickers, num_shares, shares_ratio))
        # selection = list(PriceFilter(df, VolumeSelect, min_price = min_price, max_price=max_price))
        
        final_select = []
        select_by_EMA23 = []
        select_by_EMA67 = []
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
                temp_df = Calc.MACD(temp_df)
                temp_df = Calc.MA(temp_df, [5,10,20,60,300])
                temp_df = Calc.EMA(temp_df, [67, 23])
                temp_df = Calc.calculateTOWER(temp_df)
                
                last_data = temp_df.loc[td.strftime('%Y-%m-%d')] 
                
                temp_df['OSC_Trend'] = temp_df['OSC'] > temp_df['OSC'].shift(1)
                if temp_df['TColor'][-2] == 'g' and temp_df['TColor'][-1] == 'r':
                    if all(temp_df['OSC_Trend'][-2:]):
                        if temp_df['DIF'][-1] > 0 and temp_df['MACD'][-1] > 0:
                            final_select.append(ticker)
                            if temp_df.Low[-1] >= temp_df.EMA67[-1] and temp_df.Close[-1] > temp_df.Open[-1]:
                                select_by_EMA67.append(ticker)
                            if temp_df.Low[-1] >= temp_df.EMA23[-1] and temp_df.Close[-1] > temp_df.Open[-1]:
                                select_by_EMA23.append(ticker)
                            momentums.append((ticker, Calc.Momemtum(temp_df)))
                            
                            # output figure
                            temp_df = temp_df.tail(200)
                            createPlot(td, temp_df, ticker, MACD=True, TOWER=True)
                        
            except:
                print(GetException())
        
        saveRecommand(final_select, 'TOWERWithMACD')
        sendResultTable(td, final_select, momentums, 2)
        
        saveRecommand(select_by_EMA67, 'TOWERWithMACD_EMA67')
        sendResultTable(td, select_by_EMA67, momentums, '2-1')
        
        saveRecommand(select_by_EMA23, 'TOWERWithMACD_EMA23')
        sendResultTable(td, select_by_EMA23, momentums, '2-2')
        
        select_by_EMA67_23 = list(set(select_by_EMA23).intersection(select_by_EMA67))
        saveRecommand(select_by_EMA67_23, 'TOWERWithMACD_EMA67_23')
        sendResultTable(td, select_by_EMA67_23, momentums, '2-3')
    except:
        print(GetException())
    
if __name__ == '__main__':
    main(min_price=0, max_price=50, num_shares=0, shares_ratio=1.5)
    
    