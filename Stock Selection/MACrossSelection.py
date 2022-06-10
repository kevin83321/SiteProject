__updated__ = '2021-12-22 23:09:21'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, createRecommandTable, datetime
)

import shioaji as sj

def readDataFromSJ(td, tickers):
    try:
        api = sj.Shioaji()
        api.login("F128497445", "89118217k")
        contracts = [api.Contracts.Stocks[ticker] for ticker in tickers]
        # print(contracts)
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
    except:
        print(GetException())
        import os
        os._exit(0)
    else:
        return output
            
def main(td=datetime.today(),min_price=30, max_price=200, num_shares=100, shares_ratio=1):
    try:
        # setup date
        td, last = getDateBeforeTrade(td.replace(hour=18))
        print(td, last)
        
        # setup data
        schema = getSchema('TWSE')
        table = schema['StockList']
        last_date = sorted(table.distinct("UpdateDate"))[-1]
        info_data = dict((x['Ticker'], x['Industry']+f"({x['Market'][-1]})") for x in table.find({"UpdateDate":{"$eq":last_date}, "Industry" :{"$ne":""}}) if "金融" not in x['Industry'])
        
        schema = getSchema('TWSE')
        table = schema['historicalPrice']
        data = list(table.find({'Date':{'$gte':last.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))

        sjData = readDataFromSJ(td, list(info_data.keys()))
        print(sjData[:3])
        try:
            data += sjData
        except:
            pass
        
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
        VolumeSelect = VolumeFilter(df, tickers, num_shares, shares_ratio)
        selection = list(PriceFilter(df, list(VolumeSelect), max_price, min_price))
        
        # final_select = []
        pre_3y = td + timedelta(-365*3)
        selected = []
        momentums = []
        for ticker in selection:
            try:
                temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))).set_index('Date')
                temp_df.Close = temp_df.Close.replace('--', float('nan'))
                temp_df.High = temp_df.High.replace('--', float('nan'))
                temp_df.Low = temp_df.Low.replace('--', float('nan'))
                temp_df.Open = temp_df.Open.replace('--', float('nan'))
                
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
                temp_df['Adj V'] = temp_df.Volume.apply(lambda x: int(x/1000))
                # temp_df = Calc.MACD(temp_df)
                temp_df = Calc.MA(temp_df, [20])
                temp_df = Calc.EMA(temp_df, [12])
                temp_df['Vol5MA'] = temp_df.Volume.rolling(5).mean()
                temp_df['Vol67MA'] = temp_df.Volume.rolling(67).mean()
                temp_df['VMA20'] = temp_df['Adj V'].rolling(20).mean()
                v_slope = temp_df.Vol5MA.pct_change().iloc[-1]
                
                # last_data = temp_df.loc[td.strftime('%Y-%m-%d')] 
                MACross =  temp_df.EMA12.iloc[-1] > temp_df.MA20.iloc[-1] and temp_df.EMA12.iloc[-2] <= temp_df.MA20.iloc[-2]
                v_slope_condi = v_slope > 0
                if MACross and v_slope_condi:
                    # createPlot(td, temp_df, ticker)
                    selected.append(ticker)
                    momentums.append((ticker, Calc.Momemtum(temp_df)))
            except:
                print(GetException())
        
        # saveRecommand(final_select, 'VolumeWithMACD')
        # sendResultTable(td, final_select, momentums)
        
        # saveRecommand(select_by_EMA67_23, 'VolumeWithMACD_EMA67_23')
        # sendResultTable(td, select_by_EMA67_23, momentums, '1-1')
        
        # saveRecommand(select_by_Volume5, 'VolumeWithMACD_EMA67_23_VOL5')
        # sendResultTable(td, select_by_Volume5, momentums, '1-2')
        
        # saveRecommand(select_by_Volume67, 'VolumeWithMACD_EMA67_23_VOL67')
        # sendResultTable(td, select_by_Volume67, momentums, '1-3')
        
        expend_text = "黃金交叉，有起飛的可能，可逢低布局\n"
        expend_text += "若順利起飛且未跌破5MA則續抱\n"
        expend_text += "若未起飛且K線跌出20MA則出場(損)，或虧損>10%(或個人可接受之虧損幅度)"

        # select_by_Volume5_67 = list(set(selected).intersection(select_by_Volume67))
        # print(selected)
        saveRecommand(selected, 'MACross')
        sendResultTable(td, selected, momentums, '12', expend_text, info_data)
    except:
        print(GetException())
        
    
    
if __name__ == '__main__':
    main(min_price=0, max_price=9999, num_shares=100, shares_ratio=1.5)
    # main(datetime(2022,3,22), min_price=0, max_price=9999, num_shares=100, shares_ratio=1.5)
    
    