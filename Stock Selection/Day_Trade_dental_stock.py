__updated__ = '2021-06-22 01:01:23'
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
        
        stocklist_table = getSchema('TWSE.StockList')
        last_date = sorted(stocklist_table.distinct("UpdateDate"))[-1]
        tickers = [x['Ticker'].strip() for x in stocklist_table.find({"UpdateDate":{"$eq":last_date}, "AssetType":{"$eq":"股票"}})]
        
        info_table = getSchema('Stock.Info')
        Capital_map = dict((x["股票代號"], x["已發行普通股數或TDR原股發行股數"]) for x in info_table.find({"股票代號":{"$in":tickers}}))
        
        # setup data
        table = getSchema('TWSE.historicalPrice')
        raw_data = list(table.find({'Date':{'$gte':td.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}, "Ticker":{"$in":tickers}}))
        
        last_close_map = dict((x['Ticker'], x['Close']) for x in table.find({'Date':{'$gte':last.strftime('%Y-%m-%d'), '$lte':last.strftime('%Y-%m-%d')}, "Ticker":{"$in":tickers}}))
        
        
        data = []
        while raw_data:
            tmp = raw_data.pop(0)
            tmp.pop('_id')
            for col in 'Open,High,Low,Close,Volume'.split(','):
                tmp[col] = changedType(tmp[col])
            tmp['Adj_Volume'] = int(tmp['Volume'] / 1000)
            if tmp['Adj_Volume'] >= 500:
                try:
                    tmp['Transaction'] = tmp['Volume'] / Capital_map[tmp['Ticker']]
                    tmp['Ret'] = tmp['Close'] / changedType(last_close_map[tmp['Ticker']]) - 1
                except:
                    pass
                else:
                    data.append(tmp)
                
        top_ret = [x['Ticker'] for x in sorted(data, key=lambda x: x['Ret'], reverse=True)[:100]]
        top_tran = [x['Ticker'] for x in sorted(data, key=lambda x: x['Transaction'], reverse=True)[:100]]
        top_volume = [x['Ticker'] for x in sorted(data, key=lambda x: x['Adj_Volume'], reverse=True)[:100]]
        
        tickers = list(set(top_ret).intersection(top_tran).intersection(top_volume))
        
        df = pd.DataFrame(data)
        df = df[df.Ticker.isin(tickers)]
        print(df, '\n', df.shape)
        
        
        final_select = []
        pre_3y = td + timedelta(-365*3)
        # select_by_EMA67_23 = []
        # select_by_Volume5 = []
        # select_by_Volume67 = []
        momentums = []
        for ticker in tickers:
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
                temp_df['Adj_Volume'] = temp_df['Volume'].apply(lambda x: int(x/1000))
                temp_df = Calc.MACD(temp_df)
                temp_df = Calc.MA(temp_df, [5,10,20,60,300])
                temp_df = Calc.EMA(temp_df, [67, 23])
                temp_df['Vol5MA'] = temp_df.Adj_Volume.rolling(5).mean()
                temp_df['Vol67MA'] = temp_df.Adj_Volume.rolling(67).mean()
                
                last_data = temp_df.loc[td.strftime('%Y-%m-%d')] 
                final_select.append(ticker)
                # temp_df['OSC_Trend'] = temp_df['OSC'] > temp_df['OSC'].shift(1)
                # if all(temp_df['OSC_Trend'][-3:]) and all(temp_df['OSC'][-3:] > 0):
                #     final_select.append(ticker)
                
                #     if temp_df.Close[-1] > temp_df.Open[-1]:
                #         if temp_df.Low[-1] >= temp_df.EMA67[-1]:
                #             if temp_df.Low[-1] >= temp_df.EMA23[-1]:
                #                 select_by_EMA67_23.append(ticker)
                                
                                # if temp_df.Volume[-1] > temp_df.Vol5MA[-1] * shares_ratio:
                                #     select_by_Volume5.append(ticker)
                                # if temp_df.Volume[-1] > temp_df.Vol67MA[-1] * shares_ratio:
                                #     select_by_Volume67.append(ticker)
                momentums.append((ticker, Calc.Momemtum(temp_df)))
                # output figure
                temp_df = temp_df.tail(200)
                createPlot(td, temp_df, ticker, MACD=True, extra_name='Dental Stock')
            except:
                print(GetException())
        
        saveRecommand(final_select, 'PowerfulStocks')
        sendResultTable(td, final_select, momentums, '6')
        
        # saveRecommand(select_by_EMA67_23, 'PowerfulStocks_EMA67_23')
        # sendResultTable(td, select_by_EMA67_23, momentums, '6-1')
        
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
    main()#min_price=20, max_price=200, num_shares=2000, shares_ratio=1.5)
    
    