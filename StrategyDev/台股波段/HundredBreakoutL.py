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

highProbTable = pd.read_csv(os.path.join(parent, "無腦交易","Output\HundredBreakOutL","Summary_prob_holding_tradenum.csv"), encoding='utf-8-sig')
bt_sum_Table = pd.read_csv(os.path.join(parent, "無腦交易","Output\HundredBreakOutL","Summary.csv"), encoding='utf-8-sig')


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
        for ticker in info_data.keys():#df.Ticker.unique():
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
                temp_df = temp_df.set_index("Date")
                
                temp_df['Adj V'] = temp_df.Volume.apply(lambda x: int(x/1000))
                
                
                p_condition = temp_df.Close.iloc[-1] < temp_df.Close.iloc[-101:-1].min()
                v_condition = temp_df['Adj V'].mean() > 50
                if p_condition and v_condition and bt_sum_Table[bt_sum_Table.代號==ticker]['總交易次數'].values[0] >= 10 and bt_sum_Table[bt_sum_Table.代號==ticker]['勝率%'].values[0] > 50:
                    final_select.append(ticker)
                    if ticker in highProbTable.代號:
                        highProb.append((ticker, 'Y'))
                    bt_Prob.append((ticker, bt_sum_Table[bt_sum_Table.代號==ticker]['勝率%'].values[0]))
                    holding_p.append((ticker, bt_sum_Table[bt_sum_Table.代號==ticker]['平均持倉時間(日)'].values[0]))
                    # momentums.append((ticker, Calc.Momemtum(temp_df)))
            except KeyboardInterrupt:
                import os
                os._exit(0)
            except:
                print(f'Ticker : {ticker}\t Error :', GetException())
        
        description = '無腦秘書1號'
        entry_method = '選出後隔日開盤進場'
        # expand_text = "波段交易，停利停損皆10%"
        saveRecommand(final_select, 'HundrenBreakoutL')
        print(len(final_select), final_select)
        # return
        fig_path = CreateRecommendFig(td, final_select, bt_Prob=bt_Prob, holding_p=holding_p, highProb=highProb, 
                        algo_num=1, description=description, entry_method=entry_method, take_profit_rate=10, 
                        stop_loss_rate=10, algo_name='HundrenBreakoutL')
        # return
        if len(fig_path):
            sendPhoto(f"\n{description}最新選股推薦", fig_path, useTele=False)
        else:
            sendMessage(f"\n{description}今日無推薦標的", useTele=False)
        # print(createRecommandTable(final_select, bt_Prob=bt_Prob, holding_p=holding_p, highProb=highProb))
        # sendResultTable(td, final_select, bt_Prob=bt_Prob, holding_p=holding_p, highProb=highProb, algo_num=1, expand_text=expand_text, useTele=False)#, token='hDvo7h5atlmcshug48REUqOBv1nHzm1fb6YZ9I0ZNu9')
    except:
        # print(f'ticker : {ticker}\t Error : ',GetException())
        print(f'Error : ',GetException())
        pass
    
if __name__ == '__main__':
    # main(datetime(2022,6,8), min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    main(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    
    