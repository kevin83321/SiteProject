import shioaji as sj
from BrokerOTC import requestStockList, os
from datetime import datetime, timedelta
from modules import Tele
parent = os.path.dirname(os.path.abspath(__file__))

def main(date=datetime.today()):
    
    api = sj.Shioaji(backend='http', simulation=False)#True)
    api.login(person_id='F128497445', passwd='89118217k')
    tdStr = date.strftime("%Y%m%d")
    output_path = os.path.join(parent, 'Output', tdStr)
    i = 1
    while i:
        next_day = date + timedelta(i)
        if next_day.isocalendar()[-1] > 5:
            i+=1
            continue
        next_output_path = os.path.join(parent, 'Output', next_day.strftime("%Y%m%d"))
        if not os.path.isdir(next_output_path):
            os.makedirs(next_output_path)
            break
        i+=1
        
        
    Tele().sendMessage(f"現在開始{date.strftime('%Y-%m-%d')}抓取漲停股")
    
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    tse_tickers = [x['Ticker'] for x in requestStockList(2) if x['AssetType'] in ['股票', "臺灣存託憑證(TDR)", "普通股"]]
    otc_tickers = [x['Ticker'] for x in requestStockList(4) if x['AssetType'] in ['股票', "臺灣存託憑證"]]
    limit_up_tickers = []
    len_tse = 0
    len_otc = 0
    for ticker in tse_tickers + otc_tickers:
    # for ticker in tse_tickers:
        try:
            contract = api.Contracts.Stocks[ticker]
            snapShots = api.snapshots([contract])[0]
            if snapShots['high'] == contract['limit_up']:
                if ticker in tse_tickers:
                    limit_up_tickers.append((contract['code'], 'TSE', contract['limit_up']))
                    len_tse += 1
                else:
                    limit_up_tickers.append((contract['code'], 'OTC', contract['limit_up']))
                    len_otc += 1
        except:
            pass
    # length_tse = len(limit_up_tickers)
    Tele().sendMessage(f"上市漲停股 共: {len_tse} 隻")
            
    # for ticker in otc_tickers:
    #     try:
    #         contract = api.Contracts.Stocks.OTC[ticker]
    #         snapShots = api.snapshots([contract])[0]
    #         if snapShots['high'] == contract['limit_up']:
    #             limit_up_tickers.append((contract['code'], 'OTC', contract['limit_up']))
    #     except:
    #         pass
    # length_total = len(limit_up_tickers)
    Tele().sendMessage(f"上櫃漲停股 共: {len_otc} 隻")
        
    # limit_up_tickers
    with open(os.path.join(output_path, 'up_limit_tickers.csv'), 'w') as f:
        f.writelines('代碼,市場,漲停價\n')
        for ticker, exchange,up_limit in limit_up_tickers:
            f.writelines(f'"{ticker}",{exchange},{up_limit}\n')
    api.logout()
    Tele().sendMessage(f"今日({date.strftime('%Y-%m-%d')})漲停股 共: {len_tse + len_otc} 隻")
    os._exit(0)

if __name__ == '__main__':
    main()