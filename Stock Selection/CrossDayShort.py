__updated__ = '2022-03-23 07:37:31'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, datetime
)
import shioaji as sj

def readDataFromSJ(td, tickers):
    api = sj.Shioaji()
    api.login("F128497445", "89118217k")
    contracts = [api.Contracts.Stocks[ticker] for ticker in tickers]
    snapshots = api.snapshots(contracts)
    output = []
    for data in snapshots:
        output.append({
            "Date":td.strftime("%Y-%m-%d"),
            "Ticker":data['code'],
            "Open":data['open'],
            "High":data['high'],
            "Low":data['low'],
            "Close":data['close'],
            "Volume":data["total_volume"] * 1000,
        })
    return output
            
def main(td = datetime.today(), min_price=0, max_price=50, num_shares=10000, shares_ratio=0, num_dog=11):
    try:
        # setup date
        # now = datetime.now()
        td, last = getDateBeforeTrade(td.replace(hour=18))
        # setup data
        schema = getSchema('TWSE')
        table = schema['StockList']
        last_date = sorted(table.distinct("UpdateDate"))[-1]
        info_data = dict((x['Ticker'], x['Industry']+f"({x['Market'][-1]})") for x in table.find({"UpdateDate":{"$eq":last_date}, "Industry" :{"$ne":""}}) if "金融" not in x['Industry'])
        
        schema = getSchema('TWSE')
        table = schema['historicalPrice']
        data = list(table.find({'Date':{'$gte':last.strftime('%Y-%m-%d'), '$lte':last.strftime('%Y-%m-%d')}, "Ticker" :{"$in":list(info_data.keys())}}))
        sjData = readDataFromSJ(td, list(info_data.keys()))
        try:
            data += sjData
        except:
            pass

        if datetime.now() >= td.replace(hour=15):
            data = list(table.find({'Date':{'$gte':last.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}, "Ticker" :{"$in":list(info_data.keys())}}))

        df = pd.DataFrame(data).set_index('Date')
        if len(df.index.unique()) < 2:
            data = list(table.find({'Date':{'$gte':(last+timedelta(-30)).strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
            df = pd.DataFrame(data).set_index('Date')
            df = df.loc[sorted(df.index.unique())[-2:], :]
        del df['_id']
        for col in 'Open,High,Low,Close,Volume'.split(','):
            df[col] = df[col].apply(changedType)
        df["Adj V"] = df["Volume"].apply(lambda x: int(x/1000))
        
        last_df = df.loc[sorted(df.index.unique())[-1],:].reset_index().set_index("Ticker")
        # 強勢股
        # last_df = last_df[last_df.Volume >= 1000]
        # last_df['Ret'] = 0
        # last_df["HighRet"] = 0
        # for ticker in last_df.index.unique():
        #     last_df.loc[ticker, "Ret"] = df[df.Ticker == ticker].Close.pct_change()[-1]
        #     try:
        #         last_df.loc[ticker, "HighRet"] = (df[df.Ticker == ticker].High.iloc[-1] / df[df.Ticker == ticker].Close.iloc[-2]) - 1
        #     except:
        #         pass
        # last_df = last_df.sort_values("Ret", ascending=False)[:100]
        # last_df = last_df[last_df["HighRet"] >= 0.02]
        last_df = last_df[last_df["Adj V"] >= num_shares]
        final_tickers = last_df.index
        # ticker_volume_filted = last_df.index
        
         # Foreign Table
        # f_table = schema['ForeignAndOther.Foreign']
        # # print({"Ticker":{"$in":list(ticker_volume_filted)}, "OverBS":{"$gt":0}, "Date":{"$gte":last.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}) # "Ticker":{"$in":list(ticker_volume_filted)}, 
        # f_over_b = list(f_table.find({"Ticker":{"$in":list(ticker_volume_filted)}, "OverBS":{"$gt":0}, "Date":{"$gte":last.strftime('%Y-%m-%d'), '$lt':td.strftime('%Y-%m-%d')}})) # {"Ticker":{"$in":list(ticker_volume_filted)}, "OverBS":{"$gt":0}, "Date":{"$gte":last.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}
        # # print(f_over_b)
        # final_tickers = list(set([x["Ticker"] for x in f_over_b if x['OverBS'] > 0])) #  and x['Ticker'] in list(ticker_volume_filted)
        # print(final_tickers)
        # for ticker in final_tickers:
        #     print(f"{ticker} in volume filted {ticker in ticker_volume_filted}")
        # import os
        # os._exit(0)
        final_select = []
        pre_3y = td + timedelta(-365*3)
        momentums = []
        for ticker in final_tickers:#df.Ticker.unique():
            try:
                temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}})))#.set_index('Date')
                if datetime.now() < td.replace(hour=15):
                    td_data = [x for x in sjData if x['Ticker'] == ticker]
                    if td_data:
                        # print(td_data)
                        temp_df = temp_df.append(pd.DataFrame(td_data))#.set_index("Date"))
                if temp_df is None:
                    print(ticker, 'is None', temp_df)
                    continue
                if temp_df.empty:
                    print(ticker, 'is empty', temp_df)
                    continue
                for col in 'Open,High,Low,Close,Volume'.split(','):
                    temp_df[col] = temp_df[col].apply(changedType)
                temp_df = temp_df.set_index("Date")
                
                temp_df = Calc.MA(temp_df, [5,10,20,60])
                temp_df['Adj V'] = temp_df.Volume.apply(lambda x: int(x/1000))
                if temp_df['Adj V'].iloc[-1] < 1000:
                    continue

                # temp_df['VMA5'] = temp_df['Adj V'].rolling(5).mean()
                # temp_df['VMA10'] = temp_df['Adj V'].rolling(10).mean()
                # temp_df['VMA20'] = temp_df['Adj V'].rolling(20).mean()

                # temp_df['VSlope5'] = temp_df['VMA5'].pct_change()
                # temp_df['VSlope10'] = temp_df['VMA10'].pct_change()
                # temp_df['VSlope20'] = temp_df['VMA20'].pct_change()

                temp_df['Slope5'] = temp_df['MA5'].pct_change()
                temp_df['Slope10'] = temp_df['MA10'].pct_change()
                temp_df['Slope20'] = temp_df['MA20'].pct_change()
                temp_df['Slope60'] = temp_df['MA60'].pct_change()
                # p_slope_condi = temp_df['Slope5,Slope10,Slope20,Slope60'.split(',')].min(axis=1).iloc[-1] > 0

                # temp_df['HC'] = temp_df['High'] / temp_df['Close'].shift(1) - 1
                # temp_df['HCMA'] = temp_df['HC'].rolling(5).mean()# >= .05
                # v_slope_condi = temp_df.VSlope10.iloc[-1] > 0 and temp_df.VSlope20.iloc[-1] > 0 and temp_df.VSlope5.iloc[-1] > 0
                p_slope_condi = temp_df.Slope5.iloc[-1] < 0 # temp_df.Slope10.iloc[-1] > 0 and temp_df.Slope20.iloc[-1] > 0 and 
                p_ma_condi = temp_df.MA5.iloc[-1] < temp_df.MA10.iloc[-1] and temp_df.MA10.iloc[-1] < temp_df.MA20.iloc[-1] and temp_df.MA20.iloc[-1] < temp_df.MA60.iloc[-1]
                bar_condi = temp_df.Close.iloc[-2] < temp_df.Open.iloc[-2] and temp_df.Close.iloc[-1] >= temp_df.Open.iloc[-1]
                bar_last_condi = temp_df.Low.iloc[-1] < temp_df.Low.iloc[-2] and temp_df.High.iloc[-1] < min(temp_df.MA5.iloc[-1], temp_df.Low.iloc[-2])
                bar_last2_condi = temp_df.Low.iloc[-1] < min(temp_df.Close.iloc[-1], temp_df.Open.iloc[-1]) and temp_df.High.iloc[-1] > max(temp_df.Close.iloc[-1], temp_df.Open.iloc[-1])

                # p_slope_condi = temp_df.Slope10.iloc[-2] > 0 and temp_df.Slope20.iloc[-2] > 0 and temp_df.Slope5.iloc[-2] > 0
                # p_ma_condi = temp_df.MA5.iloc[-2] > temp_df.MA10.iloc[-2] and temp_df.MA10.iloc[-2] > temp_df.MA20.iloc[-2]
                # tr_condi = temp_df['HCMA'].iloc[-1] >= .05
                # v_condi = min(temp_df['VMA5'].iloc[-1], temp_df['VMA20'].iloc[-1]) >= 5000
                # p_condi = temp_df.Close.iloc[-1] < 1000
                # pct_condi = temp_df['Close'].pct_change().iloc[-1] >= .06
                # k_condi_1 = not ((temp_df['Close'].pct_change().iloc[-1] < 0) and temp_df['Adj V'].pct_change().iloc[-1] < 0)
                # k_condi_2 = not (round(temp_df['Adj V'].pct_change().iloc[-1],2) >= 1)
                # k_condi_3 = not temp_df['Close'].iloc[-1] < temp_df['Open'].iloc[-1]
                # k_condi = all([k_condi_1, k_condi_2])
                # tmp_tick = Calc.get_minimum_tick(temp_df.Close.iloc[-1])
                # limit_condi = True
                # if (temp_df.Close.iloc[-1] + tmp_tick) / temp_df.Close.iloc[-2] > 1.1:
                #     limit_condi = False
                # if (temp_df.Close.iloc[-1] - tmp_tick) / temp_df.Close.iloc[-2] < 0.9:
                #     limit_condi = False
                # if v_slope_condi and p_slope_condi and tr_condi and v_condi and p_condi and limit_condi and k_condi and pct_condi:
                #     final_select.append(ticker)
                # if all([condi_1, condi_2, condi_3, condi_4, condi_5, condi_6, condi_7]): #, condi_8
                if p_slope_condi and p_ma_condi and bar_condi and bar_last_condi and bar_last2_condi:
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
            except KeyboardInterrupt:
                import os
                os._exit(0)
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        expand_text = "隔日'空'，收盤價買入，隔天2%停利，5%停損，皆未觸及則收盤價出"
        # expand_text = '強勢股 : 順勢而為 - 波段交易，也可能量能耗盡\n'
        # expand_text += "隔日若收高過前高可做多(若特別強勢-會漲停的那種記得掛觸價單(高於前高的位置)先進場)\n"
        # expand_text += "隔日若收沒明顯過前高，但紅K橫盤可(依舊貼近MA20)，可做多\n"
        # expand_text += "隔日若收十字或黑K，則可試空單\n"
        # expand_text += "未明顯噴發但有持續緩漲則沿著MA20續抱，連續噴2、3根的可以改看MA5或MA10\n"
        # expand_text += "收低於MA20出場"
        # expand_text += "停利 : 日K完全向下離開10MA出場"
        # expand_text += "停損 : 日K完全向下離開60MA出場，或10%停損"
        saveRecommand(final_select, 'CrossDayShort')
        print(len(final_select), final_select)
        sendResultTable(td, final_select, momentums, num_dog, expand_text=expand_text, Industry=info_data)
    except:
        # print(f'ticker : {ticker}\t Error : ',GetException())
        print(f'Error : ',GetException())
        pass
    
if __name__ == '__main__':
    # main(datetime(2022,6,8), min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    main(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    
    