

__updated__ = '2021-02-21 00:09:53'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType
)
            
def main(min_price=0, max_price=50, num_shares=10000, shares_ratio=0):
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
        df["Adj V"] = df["Volume"].apply(lambda x: int(x/1000))
        # print(df.loc[sorted(df.index.unique())[-1],:].Volume >= num_shares)

        
        last_df = df.loc[sorted(df.index.unique())[-1],:].reset_index().set_index("Ticker")
        # 強勢股
        last_df = last_df[last_df.Volume >= 500]
        last_df['Ret'] = 0
        for ticker in last_df.index.unique():
            last_df.loc[ticker, "Ret"] = df[df.Ticker == ticker].Close.pct_change()[-1]
        last_df = last_df.sort_values("Ret", ascending=False)[:100]
        last_df = last_df[last_df["Adj V"] >= num_shares]
        ticker_volume_filted = last_df.index
        
        # print(ticker_volume_filted)
        final_select = []
        pre_3y = td + timedelta(-365*3)
        momentums = []
        for ticker in ticker_volume_filted:#df.Ticker.unique():
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
                # temp_df['upslope'] = temp_df['upband'].pct_change()
                # temp_df['bandwidth'] = temp_df['upband'] / temp_df['dnband'] - 1
                
                # if temp_df['OSC'][-2] <= 0 and temp_df['OSC'][-1] >= 0:
                #     if (temp_df['DIF'][-1] >= 0) and (temp_df['MACD'][-1] >= 0):
                if temp_df['slope'][-1] >= 0.01:
                    if temp_df['Low'][-1] <= temp_df['upband'][-1] <= temp_df['High'][-1] or temp_df['Open'][-1] <= temp_df['upband'][-1] <= temp_df['Close'][-1]:
                        if temp_df['bandwidth'].pct_change()[-1] > 0:
                            final_select.append(ticker)
                            momentums.append((ticker, Calc.Momemtum(temp_df)))
                        
                            # # output figure
                            temp_df = temp_df.tail(200)
                            createPlot(td, temp_df, ticker, MACD=True, BBAND=True)
                        
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        expand_text = '開布林，斜率向上，收紅K，紅K在布林上緣 - 波段交易\n'
        # expand_text += '開布林，斜率向上，收紅K，紅K在布林上緣 - 波段交易\n'
        expand_text += "日K完全向下離開5MA出場"
        saveRecommand(final_select, 'ShortTermTrade')
        sendResultTable(td, final_select, momentums, 5, expand_text=expand_text)
    except:
        # print(f'ticker : {ticker}\t Error : ',GetException())
        print(f'Error : ',GetException())
        pass
    
if __name__ == '__main__':
    main(min_price=0, max_price=50, num_shares=10000, shares_ratio=1.5)
    
    