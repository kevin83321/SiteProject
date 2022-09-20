from Utils import (requests, pd, deepcopy, datetime, timedelta, sleep, output_path, os)
from PlotUtils import CreateTable
from Messenger.LineMessenger import LineMessenger as Line

output_path = os.path.join(output_path, "Opt_OI")
if not os.path.isdir(output_path):
    os.makedirs(output_path)

def outputRawOI(opt_df, output_, ticker):
    with pd.ExcelWriter(os.path.join(output_, f"{ticker}_Option_OI_raw.xlsx")) as writer:
        ttms = sorted(opt_df.ttm.unique())
        for ttm in ttms:
            ttm_df = opt_df[opt_df.ttm == ttm]
            tmp_df_c = ttm_df[ttm_df.c_p == "C"]
            tmp_df_p = ttm_df[ttm_df.c_p == "P"]
    
            tmp_df_c.to_excel(writer, encoding='utf-8-sig', index=False, sheet_name=ttm)
            tmp_df_p.to_excel(writer, encoding='utf-8-sig', index=False, sheet_name=ttm, startcol = 29)
            
def GetLastTwoPath(ticker='QQQ', td=datetime.today()):
    i = -1
    update_f_path = None
    last_f_path = None
    last_date = update_date = None
    print(td)
    while 1:
        last_day = td + timedelta(i)
        
        # print(last_day)
        i-=1
        output_ = os.path.join(output_path, str(last_day.year), str(last_day.month).zfill(2), str(last_day.day).zfill(2))
        f_path = os.path.join(output_, f"{ticker}_Option_OI_raw.xlsx")
        if not update_f_path:
            if os.path.isfile(f_path):
                update_f_path = f_path
                update_date = last_day
        elif not last_f_path:
            if os.path.isfile(f_path):
                last_f_path = f_path
                last_date = last_day
        if update_f_path and last_f_path:
            break
        if i < -30:
            break
    
    return last_f_path, last_date, update_f_path, update_date

def AggregateDF(xl, ttms):

    # aggregate last
    call_df = pd.DataFrame()
    call_df.index.name = 'strike'

    put_df = pd.DataFrame()
    put_df.index.name = 'strike'
    for ttm in ttms:
        tmp_df = xl[ttm]
        tmp_call_df = tmp_df['open_interest,underlying,ttm,strike,c_p'.split(',')].set_index("strike")
        tmp_put_df = tmp_df['open_interest.1,underlying.1,ttm.1,strike.1,c_p.1'.split(',')]
        tmp_put_df.columns = 'open_interest,underlying,ttm,strike,c_p'.split(',')
        tmp_put_df = tmp_put_df.set_index('strike')

        if call_df.empty:
            call_df = tmp_call_df
        else:
            for row in tmp_call_df.itertuples():
                try:
                    call_df.loc[row.Index, 'open_interest'] += row.open_interest
                except:
                    tmp_row = dict(row._asdict())
                    tmp_row['strike'] = tmp_row['Index']
                    del tmp_row['Index']
                    call_df = call_df.append(pd.DataFrame([tmp_row]).set_index('strike'))

        if put_df.empty:
            put_df = tmp_put_df
        else:
            for row in tmp_put_df.itertuples():
                try:
                    put_df.loc[row.Index, 'open_interest'] += row.open_interest
                except:
                    tmp_row = dict(row._asdict())
                    tmp_row['strike'] = tmp_row['Index']
                    del tmp_row['Index']
                    put_df = put_df.append(pd.DataFrame([tmp_row]).set_index('strike'))

    call_df = call_df.sort_values("open_interest", ascending=False)
    put_df = put_df.sort_values("open_interest", ascending=False)
    
    # print(call_df.head(10))
    # print(call_df.ttm.unique())
    # print(put_df.head(10))
    # print(put_df.ttm.unique())
    # print(call_df.open_interest.sum(), put_df.open_interest.sum())
    
    return call_df, put_df

def GetOptionOI(ticker="QQQ", update=True):
    
    #=====================
    # Read Update Data
    #=====================
    if update:
        try:
            url = f"https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker.upper()}.json"
            res = requests.get(url)
            data = res.json()
        except:
            url = f"https://cdn.cboe.com/api/global/delayed_quotes/options/_{ticker.upper()}.json"
            res = requests.get(url)
            data = res.json()
        opts_ = data['data']['options']

        #=====================
        # Setup Output Path
        #=====================
        trade_date = pd.to_datetime(data['data']['last_trade_time']) # datetime.today()
        print(f"====== {trade_date} ======")
        output_ = os.path.join(output_path, str(trade_date.year), str(trade_date.month).zfill(2), str(trade_date.day).zfill(2))
        if not os.path.isdir(output_):
            os.makedirs(output_)
        #------------------------
        # Take Update Option Info
        #------------------------
        updated_datas = []
        for opt in opts_:
            opt_symbol = opt['option']
            underlying = opt_symbol[:-15]
            strike = int(opt_symbol[-8:]) / 1000
            c_p = opt_symbol[-9:-8]
            ttm = opt_symbol[-15:-9]
    #         print(underlying, ttm, c_p, strike)
            opt.update({
                'underlying':underlying,
                'ttm':ttm,
                'strike':strike,
                'c_p':c_p
            })
            updated_datas.append(opt)

        #========================
        # Output Raw Data
        #========================
        opt_df = pd.DataFrame(updated_datas)
        outputRawOI(opt_df, output_, ticker)

    #========================
    # Read For Aggregate
    #========================
    last_f_path, last_date, update_f_path, update_date = GetLastTwoPath(ticker)
    # print(last_date)
    if not last_f_path or not last_date:
        return
    xl_last = pd.read_excel(last_f_path, None, engine='openpyxl')
    xl_update = pd.read_excel(update_f_path, None, engine='openpyxl')

    last_ttms = sorted(set([x[:4] for x in xl_last.keys()]))
    update_ttms = sorted(set([x[:4] for x in xl_update.keys()]))
    # print(last_ttms, update_ttms)
    last_near_ttms = [x for x in xl_last.keys() if x[:4] == last_ttms[0]]
    update_near_ttms = [x for x in xl_update.keys() if x[:4] == update_ttms[0]]
    # print(last_near_ttms, update_near_ttms, '\n')
    last_near2_ttms = [x for x in xl_last.keys() if x[:4] == last_ttms[1]]
    update_near2_ttms = [x for x in xl_update.keys() if x[:4] == update_ttms[1]]
    # print(last_near2_ttms, update_near2_ttms, '\n')

    if len(set(last_ttms[:2]+update_ttms[:2])) > 2:
        last_near_ttms = [x for x in xl_last.keys() if x[:4] == last_ttms[1]]
        last_near2_ttms = [x for x in xl_last.keys() if x[:4] == last_ttms[2]]
        # print(last_near_ttms, update_near_ttms, '\n')
        # print(last_near2_ttms, update_near2_ttms, '\n')

    last_call, last_put = AggregateDF(xl_last, last_near_ttms)
    update_call, update_put = AggregateDF(xl_update, update_near_ttms)
    update_call['diff'] = update_call['open_interest'] - last_call['open_interest']
    update_put['diff'] = update_put['open_interest'] - last_put['open_interest']
    # print(update_call.ttm.unique(),update_call.head(), '\n')
    near1_path = CreateTable(ticker, update_call, update_put, update_date)
    if ticker in 'QQQ,TSM,SPY,GLD,BABA,VIX,TSLA,XLF':
        SendLineNotify(ticker, update_date, near1_path, CreateInfo(data['data']))
    # print(near1_path, '\n')

    last_call2, last_put2 = AggregateDF(xl_last, last_near2_ttms)
    update_call2, update_put2 = AggregateDF(xl_update, update_near2_ttms)
    update_call2['diff'] = update_call2['open_interest'] - last_call2['open_interest']
    update_put2['diff'] = update_put2['open_interest'] - last_put2['open_interest']
    # print(update_call2.ttm.unique(),update_call2.head(), '\n')
    near2_path = CreateTable(ticker, update_call2, update_put2, update_date)
    # print(near2_path)

def CreateInfo(data):
    info = f"最新價格 : {data['current_price']}" + "\n"
    if data['symbol'] == 'QQQ':
        info += f"約當指數 = {int(data['current_price'] * 40.89)}\n"
    info += f"變動(率) : {data['price_change']}({data['price_change_percent']}%)" + "\n"
    return info

def SendLineNotify(ticker, update_date, file_path, underlying_info=''):
    msg = f"\n{ticker}選擇權近月資料整理更新【{update_date.strftime('%Y-%m-%d')}】" + '\n'
    msg += underlying_info
    # msg = "Test : " + file_path
    Line.sendPhoto(msg, file_path, token='Zk6VTsmW9iN0Kh01eYPcYH09JIuG354AGDAduebBLoZ')
    # msg = "Test : " + file_path
    # Line.sendMessage(msg, token= 'Zk6VTsmW9iN0Kh01eYPcYH09JIuG354AGDAduebBLoZ')

def main(update=True):
    for ticker in 'QQQ,TQQQ,ARKK,SMH'.split(','): # used to follow NASDAQ
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)
    #     break
    # return

    for ticker in 'SPY,IWM'.split(','): # used to follow SPY
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)
        
    for ticker in 'TSLA,BITO,COIN'.split(','): # used to follow TLSA
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)
        
    for ticker in 'TSM,ASX,SIMO,HIMX,UMC,CHT,IMOS,GRMN'.split(','): # used to follow Taiwan Stock ADR # HNHPF,GIGM,LEDS,APWC,
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)

    for ticker in 'BABA,JD,BIDU,FXI'.split(','): # used to follow BABA
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)

    for ticker in 'GLD,GDX,SLV'.split(','): # used to follow XAUUSD 黃金現貨
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)

    for ticker in 'VIX'.split(','): # used to follow VIX
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)

    for ticker in 'MSFT,AAPL,AMZN,MSI,META,NVDA'.split(','):
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)
    
    for ticker in 'XLF'.split(','): # used to follow Banks
        try:
            GetOptionOI(ticker, update)
        except Exception as e:
            print(ticker, "Failed", e)

if __name__ == '__main__':
    main()
    # main(False)
    