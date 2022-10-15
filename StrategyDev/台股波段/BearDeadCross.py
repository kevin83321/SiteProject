__updated__ = '2022-03-23 07:37:31'
from Calculator import Calculator as Calc
from PlotTools import createPlot, CreateRecommendFig
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, VolumeFilter, PriceFilter,
    changedType, datetime, os, parent, createRecommandTable, 
    sendPhoto, sendMessage
)
import time
from InvestorsHolding import getInvestorHolding

highProbTable = pd.read_csv(os.path.join(parent, "無腦交易","Output","Bear_Trend_With_MACD_Cross","Summary_prob_holding_tradenum.csv"), encoding='utf-8-sig')
bt_sum_Table = pd.read_csv(os.path.join(parent, "無腦交易","Output","Bear_Trend_With_MACD_Cross","Summary.csv"), encoding='utf-8-sig')


def main(td = datetime.today(), min_price=0, max_price=50, num_shares=10000, shares_ratio=0):
    try:
        # setup date
        # now = datetime.now()
        td, last = getDateBeforeTrade(td.replace(hour=18))
        # setup data
        schema = getSchema('TWSE')
        table = schema['StockList']
        last_date = sorted(table.distinct("UpdateDate"))[-1]
        info_data = dict((x['Ticker'], x['Industry']+f"({x['Market'][-1]})") for x in table.find({"UpdateDate":{"$eq":last_date}, "Industry" :{"$ne":""}}))
        
        schema = getSchema('TWSE')
        table = schema['historicalPrice']
        final_select = []
        pre_3y = td + timedelta(-365*1)
        momentums = []
        highProb = []
        bt_Prob = []
        holding_p = []
        InvestorOB = []
        InvestorOBF = []
        moms = []
        for ticker in info_data.keys():#df.Ticker.unique():
            if not ticker.isnumeric():continue
            try:
                temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}})))#.set_index('Date')
                if temp_df is None:
                    print(ticker, 'is None', temp_df)
                    continue
                if temp_df.empty:
                    print(ticker, 'is empty', temp_df)
                    continue
                for col in 'Open,High,Low,Close,Volume'.split(','):
                    temp_df[col] = temp_df[col].apply(changedType)
                # temp_df = temp_df.set_index("Date")
                if temp_df.Volume.iloc[-1] / 1000 < 200: continue
                # temp_df = Calc.MA(temp_df, [20, 240])
                temp_df = Calc.MA(temp_df.fillna(method='ffill'),[5, 10, 20, 60])
                temp_df = Calc.MACD(temp_df.fillna(method='ffill'))
                
                # temp_df['Adj V'] = temp_df.Volume.apply(lambda x: int(x/1000))
                
                short_trend_condi = temp_df.MA5.iloc[-1] < temp_df.MA10.iloc[-1] and temp_df.MA10.iloc[-1] < temp_df.MA20.iloc[-1] and temp_df.MA20.iloc[-1] < temp_df.MA60.iloc[-1]
                d_condi = temp_df.DIF.iloc[-1] <= temp_df.MACD.iloc[-1] and all(temp_df['DIF'].loc[temp_df.index[-5]:temp_df.index[-1]] > temp_df['MACD'].loc[temp_df.index[-5]:temp_df.index[-1]])
                # MACross1 = temp_df.Close.iloc[-2] < temp_df.EMA20.iloc[-2] and temp_df.Close.iloc[-1] > temp_df.EMA20.iloc[-1]
                # MACondi = temp_df.EMA20.iloc[-1] > temp_df.EMA240.iloc[-1]
                # MACross2 = temp_df.Close.iloc[-2] < temp_df.EMA240.iloc[-2] and temp_df.Close.iloc[-1] > temp_df.EMA240.iloc[-1]
                # MACross =  (MACross1 and MACondi) or MACross2
                # rsi_condi = temp_df.RSI14.iloc[-1] >= 50
                if short_trend_condi and d_condi:# and bt_sum_Table[bt_sum_Table.代號==ticker]['總交易次數'].values[0] >= 10 and bt_sum_Table[bt_sum_Table.代號==ticker]['勝率%'].values[0] > 50:
                    try:
                        holding = getInvestorHolding(ticker, td)
                        # holding = getInvestorHolding(ticker, last)
                        # print(holding)
                        if holding['外資持股比例'] > 5 and holding['外本比'] > 0.002:
                            InvestorOBF.append((ticker, 'Y'))
                        else:
                            InvestorOBF.append((ticker, 'N'))
                        if holding['投信持股比例'] > 5 and holding['投本比'] > 0.002:
                            InvestorOB.append((ticker, 'Y'))
                        else:
                            InvestorOB.append((ticker, 'N'))
                    except:
                        print(f'Ticker : {ticker} Check Investor\t Error :', GetException())
                        InvestorOBF.append((ticker, 'N'))
                        InvestorOB.append((ticker, 'N'))
                    moms.append((ticker, Calc.Momemtum(temp_df)))
                    final_select.append(ticker)
                    # print(ticker, temp_df.EMA20.iloc[-1], temp_df.EMA240.iloc[-1])
                    # if ticker in highProbTable.代號:
                    #     highProb.append((ticker, 'Y'))
                    # bt_Prob.append((ticker, bt_sum_Table[bt_sum_Table.代號==ticker]['勝率%'].values[0]))
                    # holding_p.append((ticker, bt_sum_Table[bt_sum_Table.代號==ticker]['平均持倉時間(日)'].values[0]))
                    # momentums.append((ticker, Calc.Momemtum(temp_df)))
                    time.sleep(5)
            except KeyboardInterrupt:
                import os
                os._exit(0)
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        description = '無腦秘書4號，空頭排列，MACD死亡交叉 => 做空\n'
        entry_method = '選出後隔日開盤進場，進場守前低(低於當下價格的反轉處)'
        # expand_text = "波段交易，停利停損皆10%"
        if len(final_select) >= 50:
            moms = sorted(moms, key=lambda x: x[1])[-50:]
            final_select = [x[0] for x in moms]
            InvestorOBF = [x for x in InvestorOBF if x[0] in final_select]
            InvestorOB = [x for x in InvestorOB if x[0] in final_select]
        saveRecommand(final_select, 'BearDeadCross')
        print(len(final_select), final_select)
        # return
        fig_path = CreateRecommendFig(td, final_select, bt_Prob=bt_Prob, holding_p=holding_p, highProb=highProb, 
                                        InvestorOB=InvestorOB, InvestorOBF=InvestorOBF,
                                        algo_num=4, description=description, entry_method=entry_method, take_profit_rate=10, 
                                        stop_loss_rate=10, algo_name='BearDeadCross')
        if len(fig_path) and final_select:
            sendPhoto(f"\n{description}最新選股推薦", fig_path, useTele=False)
        else:
            sendMessage(f"\n{description}今日無推薦標的", useTele=False)
    except:
        # print(f'ticker : {ticker}\t Error : ',GetException())
        print(f'Error : ',GetException())
        pass
    
if __name__ == '__main__':
    # main(datetime(2022,6,8), min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    main(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    
    