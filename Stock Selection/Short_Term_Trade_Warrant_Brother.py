__updated__ = '2021-12-28 21:30:56'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, datetime
)
            
def main(td = datetime.today(), min_price=0, max_price=50, num_shares=10000, shares_ratio=0):
    try:
        # setup date
        now = datetime.now()
        td, last = getDateBeforeTrade(td.replace(hour=now.hour))
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
        
        # print(df.loc[sorted(df.index.unique())[-1],:].Volume >= num_shares)

        
        last_df = df.loc[sorted(df.index.unique())[-1],:].reset_index().set_index("Ticker")
        # 強勢股
        last_df = last_df[last_df.Volume >= 1000]
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
                # temp_df = Calc.MACD(temp_df)
                temp_df = Calc.DI(temp_df)
                temp_df = Calc.MA(temp_df, [5, 10, 20, 60, 150], 'Close')
                # temp_df = Calc.EMA(temp_df, [67, 23])
                # temp_df = Calc.calculateTOWER(temp_df)
                # temp_df = Calc.BBAND(temp_df, 20, 2)
                temp_df['slope'] = temp_df['MA20'].pct_change()
                temp_df['Adj V'] = temp_df.Volume.apply(lambda x: int(x/1000))
                temp_df['VMA5'] = temp_df['Adj V'].rolling(5).mean()
                # temp_df['upslope'] = temp_df['upband'].pct_change()
                # temp_df['bandwidth'] = temp_df['upband'] / temp_df['dnband'] - 1
                v_ratio = (temp_df['Adj V'].iloc[-1] / temp_df['Adj V'].iloc[-2])
                
                condi_1 = temp_df.VMA5.iloc[-1] >= 1000
                condi_2 = temp_df.MA5.iloc[-1] > temp_df.MA10.iloc[-1]
                condi_3 = temp_df.MA10.iloc[-1] > temp_df.MA20.iloc[-1]
                condi_4 = 1.5 <= v_ratio and v_ratio <= 5
                condi_5 = temp_df.slope.iloc[-1] > 0
                # condi_6 = (temp_df.Low.iloc[-1] / temp_df.MA60 - 1) < 0.03 or (temp_df.Low.iloc[-1] / temp_df.MA150 - 1) < 0.03
                # if all([eval(f'condi_{i}') for i in range(1,5)]):
                if all([condi_1, condi_2, condi_3, condi_4, condi_5]):
                    final_select.append(ticker)
                    momentums.append((ticker, Calc.Momemtum(temp_df)))
                # if temp_df['OSC'][-2] <= 0 and temp_df['OSC'][-1] >= 0:
                #     if (temp_df['DIF'][-1] >= 0) and (temp_df['MACD'][-1] >= 0):
                # if temp_df['slope'][-1] >= 0:
                #     if (temp_df['Low'][-1] <= temp_df['upband'][-1] and temp_df['upband'][-1] <= temp_df['High'][-1]) or (temp_df['Open'][-1] <= temp_df['upband'][-1] and temp_df['upband'][-1] <= temp_df['Close'][-1]):
                #         if temp_df['bandwidth'].pct_change()[-1] > 0 and (temp_df['Low'][-1] / temp_df["EMA67"][-1] - 1) <= .1:
                            # final_select.append(ticker)
                            # momentums.append((ticker, Calc.Momemtum(temp_df)))
                        
                            # # output figure
                            # temp_df = temp_df.tail(200)
                            # createPlot(td, temp_df, ticker, MACD=True, BBAND=True)
                        
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        expand_text = '強勢股 : 順勢而為 - 波段交易，也可能量能耗盡\n'
        expand_text += "隔日若收高過前高可做多(若特別強勢-會漲停的那種記得掛觸價單(高於前高的位置)先進場)\n"
        expand_text += "隔日若收沒明顯過前高，但紅K橫盤可(依舊貼近MA20)，可做多\n"
        expand_text += "隔日若收十字或黑K，則可試空單\n"
        expand_text += "未明顯噴發但有持續緩漲則沿著MA20續抱，連續噴2、3根的可以改看MA5或MA10\n"
        expand_text += "收低於MA20出場"
        # expand_text += "停利 : 日K完全向下離開10MA出場"
        # expand_text += "停損 : 日K完全向下離開60MA出場，或10%停損"
        saveRecommand(final_select, 'ShortTermTrade')
        sendResultTable(td, final_select, momentums, 5, expand_text=expand_text, Industry=info_data)
    except:
        # print(f'ticker : {ticker}\t Error : ',GetException())
        print(f'Error : ',GetException())
        pass
    
if __name__ == '__main__':
    # main(datetime(2021,11,30), min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    main(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    
    