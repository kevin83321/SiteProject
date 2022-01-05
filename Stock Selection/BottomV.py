

__updated__ = '2021-12-24 00:55:52'
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
        table = schema['StockList']
        last_date = sorted(table.distinct("UpdateDate"))[-1]
        info_data = dict((x['Ticker'], x['Industry']+f"({x['Market'][-1]})") for x in table.find({"UpdateDate":{"$eq":last_date}}))
        
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
        df = df[df["Adj V"] >= num_shares]
        # print(df.loc[sorted(df.index.unique())[-1],:].Volume >= num_shares)

        
        # last_df = df.loc[sorted(df.index.unique())[-1],:].reset_index().set_index("Ticker")
        # 強勢股
        # last_df = last_df[last_df.Volume >= 500]
        # last_df['Ret'] = 0
        # for ticker in last_df.index.unique():
        #     last_df.loc[ticker, "Ret"] = df[df.Ticker == ticker].Close.pct_change()[-1]
        # last_df = last_df.sort_values("Ret", ascending=False)[:100]
        # last_df = last_df[last_df["Adj V"] >= num_shares]
        # ticker_volume_filted = last_df.index
        
        # print(ticker_volume_filted)
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
                temp_df['MaxOC'] = temp_df[['Open', 'Close']].max(axis=1)
                temp_df['MinOC'] = temp_df[['Open', 'Close']].min(axis=1)
                # temp_df = Calc.MACD(temp_df)
                # temp_df = Calc.MA(temp_df, [5, 20])
                # temp_df = Calc.EMA(temp_df, [67, 23])
                # temp_df = Calc.BBAND(temp_df, 20, 2)
                # temp_df['slope_20'] = temp_df['MA20'].pct_change()
                # temp_df['slope_5'] = temp_df['MA5'].pct_change()
                # temp_df['upslope'] = temp_df['upband'].pct_change()
                # temp_df['bandwidth'] = temp_df['upband'] / temp_df['dnband'] - 1
                
                condi_1 = temp_df.Open.iloc[-3] > temp_df.Close.iloc[-3]
                condi_2 = temp_df.MaxOC.iloc[-2] < min(temp_df.MinOC.iloc[-3], temp_df.MinOC.iloc[-1])
                # condi_3 = temp_df.MinOC.iloc[-1] > temp_df.MaxOC.iloc[-2]
                condi_4 = (temp_df.Volume.iloc[-1] / temp_df.Volume.iloc[-2]) > shares_ratio
                condi_5 = max(temp_df.Open.iloc[-1], temp_df.MinOC.iloc[-3]) < temp_df.Close.iloc[-1]
                # condi_1 = temp_df['slope_20'][-2] < 0# and temp_df['slope_5'][-2] < 0
                # condi_2 = temp_df['Low'][-2] <= temp_df['dnband'][-2] <= temp_df['High'][-2] or (temp_df['Low'][-2] > temp_df['dnband'][-2] and temp_df['Low'][-2] / temp_df['dnband'][-2] - 1 <= 0.05)
                # condi_3 = temp_df['Low'][-1] >= max(temp_df['dnband'][-1], temp_df["EMA67"][-1])
                # condi_4 = temp_df['Close'].pct_change()[-1] > 0
                # condi_5 = temp_df['slope_5'][-1] > 0
                if all([condi_1, condi_2, condi_4, condi_5]): # , condi_3
                    final_select.append(ticker)
                    momentums.append((ticker, Calc.Momemtum(temp_df)))
                            
                    # # output figure
                    # temp_df = temp_df.tail(200)
                    # createPlot(td, temp_df, ticker, MACD=True, BBAND=True)
                        
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        expand_text = '打底V轉(孤島晨星) - 波段交易\n'
        # expand_text += '開布林，斜率向上，收紅K，紅K在布林上緣 - 波段交易\n'
        expand_text += "停利 : 波段走勢啟動後，日K完全向下離開10MA出場"
        expand_text += "停損 : 向下跌破60MA"
        saveRecommand(final_select, 'BottomV')
        sendResultTable(td, final_select, momentums, 10, expand_text=expand_text, Industry=info_data)
    except:
        # print(f'ticker : {ticker}\t Error : ',GetException())
        print(f'Error : ',GetException())
        pass
    
if __name__ == '__main__':
    main(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    # main(min_price=0, max_price=50, num_shares=10000, shares_ratio=1.5)
    
    