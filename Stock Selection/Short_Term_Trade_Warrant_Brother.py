

__updated__ = '2021-02-21 00:09:53'
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
        
        
        final_select = []
        pre_3y = td + timedelta(-365*3)
        momentums = []
        for ticker in df.Ticker.unique():
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
                temp_df = Calc.MA(temp_df, [20])
                # temp_df = Calc.EMA(temp_df, [67, 23])
                # temp_df = Calc.calculateTOWER(temp_df)
                temp_df = Calc.BBAND(temp_df, 20, 2)
                temp_df['slope'] = temp_df['MA20'].pct_change()
                
                if temp_df['OSC'][-2] <= 0 and temp_df['OSC'][-1] >= 0:
                    if (temp_df['DIF'][-1] >= 0) and (temp_df['MACD'][-1] >= 0):
                        if temp_df['slope'][-1] >= 0.01:
                            if temp_df['Low'][-1] <= temp_df['upband'][-1] <= temp_df['High'][-1] or temp_df['upband'][-1] <= temp_df['Low'][-1]:
                                if temp_df['bandwidth'].pct_change()[-1] > 0:
                                    final_select.append(ticker)
                                    momentums.append((ticker, Calc.Momemtum(temp_df)))
                                
                                    # # output figure
                                    temp_df = temp_df.tail(200)
                                    createPlot(td, temp_df, ticker, MACD=True, BBAND=True)
                        
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        expand_text = '合併兩位前輩的短線選股'
        saveRecommand(final_select, 'ShortTermTrade')
        sendResultTable(td, final_select, momentums, 5, expand_text=expand_text)
    except:
        print(f'ticker : {ticker}\t Error : ',GetException())
    
if __name__ == '__main__':
    main(min_price=0, max_price=50, num_shares=0, shares_ratio=1.5)
    
    