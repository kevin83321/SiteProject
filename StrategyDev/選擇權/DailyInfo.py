from DataIO import *
from Utils import *
from OptionFunc import getNextTTM, checkClosed2TTM, calculate_atm_strike
from PlotTools import CreateTable

from Messenger.LineMessenger import LineMessenger as Line

def SendLineNotify(update_date, file_path, underlying_info=''):
    msg = f"\n台指選擇權每日資料整理更新【{update_date.strftime('%Y-%m-%d')}】" + '\n'
    Line.sendPhoto(msg, file_path, token='Zk6VTsmW9iN0Kh01eYPcYH09JIuG354AGDAduebBLoZ')

def calculateIV(df, date, h_df):
    df = df.copy(deep=True).reset_index()
    rf = 1e-2
    ttm = getNextTTM(date)
    exist_d = len([x for x in pd.date_range(date, ttm) if x.isocalendar()[-1] <= 5])
    underlying = h_df.Close.iloc[-1]
    df['IV'] = 0
    for row in df.itertuples():
        bid = row.BestBid_last if row.BestBid_last != '-' else '0.1'
        ask = row.BestAsk_last if row.BestAsk_last != '-' else '0.1'
        premium = float(row.Close_last) if row.Close_last != '-' else (float(bid) + float(ask)) / 2
        if np.isnan(premium):
            premium = row.Settle_last
        if np.isnan(premium):
            premium = row.Settle_pre
        if row.CP == 'Call':
            opt = CallOption(underlying, int(row.Strike), TimeToMaturity=exist_d, RiskFreeRate=rf, Premium=premium)#, UnderType="FUT")
        else:
            opt = PutOption(underlying, int(row.Strike), TimeToMaturity=exist_d, RiskFreeRate=rf, Premium=premium)#, UnderType="FUT")
        df.loc[row.Index, 'IV'] = opt.Sigma
    return df

def takeOIInfo(df_opt_daily, output, atm, cp_type="Call", closed2TTM=False):
    # idx_price = str(int(idx_price))
    tmp_ = df_opt_daily[df_opt_daily.CP == cp_type].set_index("Strike").fillna(0)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df_opt_daily)
    # print(tmp_)
    # print(len(set(tmp_.index)), len(list(tmp_.index)))
    tmp_ = tmp_.reindex([x for x in list(set(tmp_.index)) if x[-2:] != '50']).sort_index()
    tmp_.OI_last = tmp_.OI_last.astype(int)
    tmp_.OI_Diff = tmp_.OI_Diff.astype(int)
    if cp_type == "Call":
        output[f"{eng2chi[cp_type]}隱波-價內"] = round(tmp_[tmp_.index <= str(atm)]["IV"][-2] * 100, 2)
        output[f"{eng2chi[cp_type]}隱波-價平"] = round(tmp_[tmp_.index <= str(atm)]["IV"][-1] * 100, 2)
        output[f"{eng2chi[cp_type]}隱波-價外"] = round(tmp_[tmp_.index >= str(atm)]["IV"][1] * 100, 2)
    else:
        output[f"{eng2chi[cp_type]}隱波-價外"] = round(tmp_[tmp_.index <= str(atm)]["IV"][-2] * 100, 2)
        output[f"{eng2chi[cp_type]}隱波-價平"] = round(tmp_[tmp_.index <= str(atm)]["IV"][-1] * 100, 2)
        output[f"{eng2chi[cp_type]}隱波-價內"] = round(tmp_[tmp_.index >= str(atm)]["IV"][1] * 100, 2)
    # print(output)

    output[f"{eng2chi[cp_type]}"]["價平增減幅"] = {"履約價":str(atm), "口數":int(tmp_.loc[str(atm), "OI_Diff"])}
    # 價內
    tmp_itm = tmp_[tmp_.index <= str(atm)].sort_values("OI_Diff")
    try:
        output[f"{eng2chi[cp_type]}"]["價內最大增幅"] = {"履約價":tmp_itm.index[-1], "口數":int(tmp_itm['OI_Diff'][-1])}
    except:
        output[f"{eng2chi[cp_type]}"]["價內最大增幅"] = {"履約價":float('nan'), "口數":tmp_itm['OI_Diff'][-1]}
    # 最大未平倉
    
    tmp_max = tmp_.sort_values("OI_last")
    output[f"{eng2chi[cp_type]}"]["最大未平倉"] = {"履約價":tmp_max.index[-1], "口數":int(tmp_max['OI_last'][-1])}
    # 最大增減幅
    tmp_ = tmp_.sort_values("OI_Diff")
    
    output[f"{eng2chi[cp_type]}"]["未平倉最大增幅"] = {"履約價":tmp_.index[-1], "口數":int(tmp_['OI_Diff'][-1])}
    output[f"{eng2chi[cp_type]}"]["未平倉最大減幅"] = {"履約價":tmp_.index[0], "口數":int(tmp_['OI_Diff'][0])}


def main(date = datetime.today()):
    # ================
    # TAIFEX Data
    # ================
    df_opt_daily, last_date = getOptDailyMarketReport(date)#, update=True)
    df_pc_ratio = crawlPCRatio(last_date)
    df_insti = crawlInstitutionTraded(last_date)
    df_large_traded = crawlLargeTraded(last_date)

    # =======================
    # Historical Data - Index
    # =======================
    h_df = readIndexData(Connect2Mongo(), last_date)
    df_vol = pd.DataFrame([{"歷史波動率_20天":round(h_df['vol_20'].iloc[-1]*260**.5 * 100, 2),
                        "歷史波動率_60天":round(h_df['vol_60'].iloc[-1]*260**.5 * 100, 2),
                        "歷史波動率_260天":round(h_df['vol_260'].iloc[-1]*260**.5 * 100, 2)}])

    df_h_f = readFutureData(Connect2Mongo('TAIFEX.Interday.Future'), last_date)
    
    # =======================
    # Summary
    # =======================
    underlying = int(h_df.Close.iloc[-1])
    fut_close = 0
    try:
        fut_close = df_h_f["Close"][0]
    except:
        fut_close = df_h_f["Close"].values[0]
    output = {
        "日期":last_date.strftime("%Y-%m-%d"),
        "現貨收盤價":underlying,
        "期貨收盤價":fut_close,
        "期貨現貨價差":round(fut_close-int(underlying), 2),
        "P/C Ratio":round(float(df_pc_ratio.loc[0, '買賣權未平倉量比率%']) / 100, 4),
        '買權隱波-價內':0,
        '買權隱波-價平':0,
        '買權隱波-價外':0,
        '賣權隱波-價內':0,
        '賣權隱波-價平':0,
        '賣權隱波-價外':0,
        "歷史波動率_20天":df_vol.loc[0, "歷史波動率_20天"],
        "歷史波動率_60天":df_vol.loc[0, "歷史波動率_60天"],
        "歷史波動率_260天":df_vol.loc[0, "歷史波動率_260天"],
        "買權":{
            "最大未平倉":{
                "履約價":0,
                "口數":0
            },
            "未平倉最大增幅":{
                "履約價":0,
                "口數":0
            },
            "未平倉最大減幅":{
                "履約價":0,
                "口數":0
            },
            "價平增減幅":{
                "履約價":0,
                "口數":0
            },
            "價內最大增幅":{
                "履約價":0,
                "口數":0
            }
        },
        "賣權":{
            "最大未平倉":{
                "履約價":0,
                "口數":0
            },
            "未平倉最大增幅":{
                "履約價":0,
                "口數":0
            },
            "未平倉最大減幅":{
                "履約價":0,
                "口數":0
            },
            "價平增減幅":{
                "履約價":0,
                "口數":0
            },
            "價內最大增幅":{
                "履約價":0,
                "口數":0
            }
        },
        "三大法人_未平倉":{
            "自營商":{
                "買權":0,
                "賣權":0,
            },
            "投信":{
                "買權":0,
                "賣權":0,
            },
            "外資":{
                "買權":0,
                "賣權":0,
            },
            "合計":{
                "買權":0,
                "賣權":0,
            }
        },
        "十大_未平倉":{
            "交易人":{
                "近月":{
                    "買權":0,
                    "賣權":0,
                },
                "全月":{
                    "買權":0,
                    "賣權":0,
                }
            },
            "特法":{
                "近月":{
                    "買權":0,
                    "賣權":0,
                },
                "全月":{
                    "買權":0,
                    "賣權":0,
                }
            }
        }
    }
    
    # Calcualte Implied Volatility
    df_opt_daily = calculateIV(df_opt_daily, last_date, h_df)

    closed2TTM = checkClosed2TTM(last_date)
    atm, spacing = calculate_atm_strike(underlying, "TXO", closed2TTM)

    # 整理IV, OI
    for cp_type in df_opt_daily.CP.unique():
        takeOIInfo(df_opt_daily, output, atm, cp_type, closed2TTM)

    # 整理三大法人
    for row in df_insti.itertuples():
        output["三大法人_未平倉"][row.身分別][row.權別] = int(row._4.replace(',',''))
        output["三大法人_未平倉"]["合計"][row.權別] += int(row._4.replace(',',''))

    # 整理大額交易人
    for row in df_large_traded.itertuples():
        if row._2 == '-': continue
        if row._2.isnumeric():
            TTM_ = '近月'
        else:
            TTM_ = '全月'
        large_b = int(row._3.split('(')[0])
        special_b = int(row._3.split('(')[1][:-1])
        large_s = int(row._4.split('(')[0])
        special_s = int(row._4.split('(')[1][:-1])

        output['十大_未平倉']["交易人"][TTM_][row.契約[-2:]] = large_b - large_s
        output['十大_未平倉']["特法"][TTM_][row.契約[-2:]] = special_b - special_s

    
    saveDailyInfo(last_date, output)
    f_path = CreateTable(output)
    SendLineNotify(last_date, f_path)

if __name__ == '__main__':
    main()