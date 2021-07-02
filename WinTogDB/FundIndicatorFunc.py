# Reference : http://www.cmoney.com.tw/S2_formula.asp
# Create : 2021-03-19

__updated__ = "2021-06-30 01:36:59"

from FundDataFunc import *

__str__ = """
資產負債表
 - 資產總計(資產總額)
 - 固定資產(非流動資產合計)
 - 股東權益(權益總額)
 - 長期負債(非流動負債合計)
 - 負債總計(負債總額)
 - 流動資產(流動資產合計)
 - 流動負債(流動負債合計)
 - 存貨(存貨合計)
 - 預付費用及預付款(預付款項合計)
 - 短期借款(短期借款合計)
 - 應收帳款與票據(應收帳款淨額)
 - 應付帳款(應付帳款合計)
現金流量表
 - 現金及約當現金(期末現金及約當現金餘額)
 - 稅前純益(本期稅前淨利（淨損）)
 - 支付之利息
 - 折舊費用
 - 攤銷費用
 - 利息費用
 - 利息收入
 - 其他投資活動
 - 投資活動之淨現金流入（流出）
綜合損益表
 - 稅後純益(本期淨利（淨損）)
 - 營業收入淨額(營業收入合計)
 - 銷貨成本(銷貨成本合計)
 - 營業成本(營業成本合計)
 - 營業毛利(營業毛利（毛損）淨額)
 - 營業利益(營業利益（損失）)
 - 研發費用(研究發展費用合計)
 - 管銷費用(推銷費用合計 + 管理費用合計)
 - 營業費用(營業費用合計)
# 金融業財報 : 相關項目 https://goodinfo.tw/StockInfo/StockFinDetail.asp?RPT_CAT=BS_M_QUAR&STOCK_ID=2801
"""

def FindKeys(data, target=None):
    for key in data.keys():
        print(key, key == target)

def FixedAssetsRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_RATIO
    固定資產比率 = 固定資產/資產總計
    """
    FixedAsset = GetFixedAsset(data)
    TotalAsset = GetTotalAsset(data)
    return FixedAsset / TotalAsset * 100

def FixedAssetsEquityRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_EQUITY_RATIO
    固定資產對股東權益比率(%) = 固定資產(千) / 股東權益(千)
    """
    FixedAsset = GetFixedAsset(data)
    TotalRights = GetTotalRights(data)
    return FixedAsset / TotalRights * 100

def FixedAssetsLongTermDebtRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_LONG_TERM_DEBT_RATIO
    固定資產對長期負債比率(%) = 固定資產(千) / 長期負債(千)
    """
    FixedAsset = GetFixedAsset(data)
    LongTermDebt = GetLongTermDebt(data)
    return FixedAsset / LongTermDebt * 100 if LongTermDebt else float('nan')

def FixedAssetsLongTermFundsRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_LONG_TERM_FUNDS_RATIO
    固定資產對長期資金比率(%) = 固定資產(千) / (股東權益(千) + 長期負債(千))
    """
    FixedAsset = GetFixedAsset(data)
    TotalRights = GetTotalRights(data)
    LongTermDebt = GetLongTermDebt(data)
    return FixedAsset / (TotalRights + LongTermDebt) * 100

def LiabilityRatio(data) -> float:
    """
    TODO: calculate LIABILITY_RATIO
    負債比率(%)	= 負債總計(千) / 資產總計(千)
    """
    TotalDebt = GetTotalDebt(data)
    TotalAsset = GetTotalAsset(data)
    return TotalDebt / TotalAsset * 100

def LongTermFundsFixedsAssetsRatio(data) -> float:
    """
    TODO: calculate LONG_TERM_FUNDS_FIXED_ASSETS_RATIO
    長期資金佔固定資產比率 = (股東權益(千) + 長期負債(千)) / 固定資產(千)
    """
    return 1 / FixedAssetsLongTermFundsRatio(data) * 100

def EquityLiabilityRatio(data):
    """
    TODO: calculate EQUITY_LIABILITY_RATIO
    股東權益對負債比率(%) = 股東權益(千) / 負債總計(千)
    """
    TotalRights = GetTotalRights(data)
    TotalDebt = GetTotalDebt(data)
    return TotalRights / TotalDebt * 100

def EquityLongTermDebtRatio(data):
    """
    TODO: calculate EQUITY_LONG_TERM_DEBT_RATIO
    股東權益對長期負債比率(%) = 股東權益(千) / 長期負債(千)
    """
    TotalRights = GetTotalRights(data) 
    LongTermDebt = GetLongTermDebt(data)
    return TotalRights / LongTermDebt * 100 if LongTermDebt else float('nan')

def CapitalTotalAssetsRatio(data):
    """
    TODO: calculate CAPITAL_TOTAL_ASSETS_REATIO
    運用資本對資產總額比率(%) = (流動資產(千) - 流動負債(千)) / 資產總計(千)
    """
    TotalAsset = GetTotalAsset(data)
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    return (FlowAsset - FlowDebt) / TotalAsset * 100

def NetRatio(data):
    """
    TODO: calculate NET_RATIO
    淨值比率 = 股東權益(千) / 資產總計(千)
    """
    TotalRights = GetTotalRights(data)
    TotalAsset = GetTotalAsset(data)
    return TotalRights / TotalAsset * 100

def LongTermDebtNetRatio(data):
    """
    TODO: calculate LONG_TERM_DET_NET_RATIO
    長期負債對淨值比率(%) = 長期負債(千) / 股東權益(千)
    """
    return 1 / EquityLongTermDebtRatio(data)  * 100

def FixedAssetsNetRatio(data):
    """
    TODO: calculate FIXED_ASSETS_NET_RATIO
    固定資產對淨值比率(%) = 固定資產(千) / 股東權益(千)
    """
    return FixedAssetsRatio(data) * 100

def LeverageRatio(data):
    """
    TODO: calculate LEVERAGE_RATIO
    槓桿比率(%) = 負債總計(千) / 股東權益(千)
    """
    TotalDebt = GetTotalDebt(data)
    TotalRights = GetTotalRights(data)
    return TotalDebt / TotalRights * 100

def CurrentRatio(data):
    """
    TODO: calculate CURRENT_RATIO
    流動比率(%) = 流動資產(千) / 流動負債(千)
    """
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    return FlowAsset / FlowDebt * 100 if FlowDebt else float('nan')

def QuickRatio(data) -> float:
    """
    TODO: calculate QUICK_RATIO
    速動比率(%) = (流動資產(千) - 存貨(千) - 預付費用及預付款(千)) / 流動負債(千)
    """
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    try:
        if '存貨合計' in data['資產負債表']:
            Inventory = float(data['資產負債表']['存貨合計']['Value'])
        else:
            Inventory = float(data['資產負債表']['存貨']['Value'])
    except:
        Inventory = 0 
    try:
        if '預付款項合計' in data['資產負債表']:
            PrePayment = float(data['資產負債表']['預付款項合計']['Value'])
        else:
            PrePayment = float(data['資產負債表']['預付款項']['Value'])
    except:
        PrePayment = sum([float(data['現金流量表'][key]['Value']) for key in '預付設備款增加,其他預付款項增加,長期預付租金'.split(',') if key in data['現金流量表'].keys()])
        # PrePayment = float(data['現金流量表']['預付設備款增加']['Value'])#其他預付款項增加
        # PrePayment += float(data['現金流量表']['其他預付款項增加']['Value'])#其他預付款項增加
    
    return (FlowAsset - Inventory - PrePayment) / FlowDebt * 100 if FlowDebt else float('nan')

def Cash2CurrentAssetsRatio(data) -> float:
    """
    TODO: calculate CASH_TO_CURRENT_ASSETS_RATIO
    現金與流動資產比率(%) = 現金及約當現金(千) / 流動資產(千)
    """
    FlowAsset = GetFlowAsset(data)
    Cash = GetCash(data)
    return Cash / FlowAsset * 100

def Cash2CurrentLiabilityRatio(data) -> float:
    """
    TODO: calculate CASH_TO_CURRENT_LIABILITY_RATIO
    現金與流動負債比率(%) = 現金及約當現金(千) / 流動負債(千)
    """
    FlowDebt = GetTotalFlowDebt(data)
    Cash = GetCash(data)
    return Cash / FlowDebt * 100 if FlowDebt else float('nan')

def Capital2CurrentDFlowDebtsRatio(data) -> float:
    """
    TODO: calculate CAPITAL_TO_CURRENT_ASSETS_RATIO
    運用資本與流動資產比率(%) = (流動資產(千) - 流動負債(千)) / 流動資產(千)
    """
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    return (FlowAsset - FlowDebt) / FlowAsset * 100 if FlowAsset else float('nan')
    

def ShortTermBorrowing2CurrentAssetsRatio(data):
    """
    TODO: calculate SHORT_TERM_BORROWING_TO_CURRENT_ASSETS_RATIO
    短期借款與流動資產比率(%) = 短期借款(千) / 流動資產(千)
    """
    FlowAsset = GetFlowAsset(data)
    try:
        try:
            if '短期借款合計' in data['資產負債表'].keys():
                ShortDebt = float(data['資產負債表']['短期借款合計']['Value'])
            else:
                ShortDebt = float(data['資產負債表']['短期借款']['Value'])
        except:
            ShortDebt = float(data['現金流量表']['短期借款增加']['Value']) - float(data['現金流量表']['短期借款減少']['Value'])
    except:
        return 0
    else:
        return ShortDebt / FlowAsset * 100 if FlowAsset else float('nan')

def PayablesTurnoverRatio(pre_data, update_data):
    """
    TODO: calculate PAYABLES_TURNOVER_RATIO
    應付款項週轉率(%) = 銷貨成本 / 平均應付帳款
    """
    try:
        if '應付帳款合計' in update_data['資產負債表'].keys():
            Payables = float(update_data['資產負債表']['應付帳款合計']['Value'])
        else:
            Payables = float(update_data['資產負債表']['應付帳款']['Value'])
    except:
        Payables = sum([float(value['Value']) for key, value in update_data['資產負債表'].items() if '應付' in key and not '費用' in key])

    try:        
        try:
            if '銷貨成本合計' in update_data['綜合損益表'].keys():
                CostofSales = float(update_data['綜合損益表']['銷貨成本合計']['Value'])
            else:
                CostofSales = float(update_data['綜合損益表']['銷貨成本']['Value'])
        except:
            try:
                if '存貨合計' in pre_data['資產負債表'].keys():
                    PreInventory = float(pre_data['資產負債表']['存貨合計']['Value'])
                else:
                    PreInventory = float(pre_data['資產負債表']['存貨']['Value'])
            except:
                # print(pre_data['資產負債表'].keys())
                pass
                
            try:
                AdjInventory = float(update_data['現金流量表']['存貨（增加）減少']['Value'])
            except:
                AdjInventory = float(update_data['現金流量表']['存貨減少(增加)之調整數']['Value'])
                
            if '存貨合計' in update_data['資產負債表'].keys():
                CurrentInventory = float(update_data['資產負債表']['存貨合計']['Value'])
            else:
                CurrentInventory = float(update_data['資產負債表']['存貨']['Value'])
            CostofSales = PreInventory + AdjInventory - CurrentInventory
    except:
        return float('nan')
    return CostofSales / Payables * 100 if Payables else float('nan')

def ReceivableTurnoverRatio(data):
    """
    TODO: calculate REVEIVABLE_TURNOVER_RATIO
    應收款項週轉率(%) = 營業收入淨額(千) / 應收帳款與票據(千)
    // 應收款項週轉天數 = 360 / (營業收入淨額(千) / 應收帳款與票據(千))
    """
    Receivable = 0
    try:
        Receivable += float(data['資產負債表']['應收帳款淨額']['Value'])
    except:
        try:
            Receivable += float(data['資產負債表']['應收帳款']['Value'])
        except:
            try:
                Receivable += float(data['資產負債表']['應收帳款－關係人淨額']['Value'])
            except:
                pass
            try:
                Receivable += float(data['現金流量表']['應收帳款－關係人（增加）減少']['Value'])
            except:
                pass
            try:
                Receivable += float(data['現金流量表']['應收帳款（增加）減少']['Value'])
            except:
                pass
    Revenue = GetRevenue(data)
    return Revenue / Receivable * 100 if Receivable else float('nan')

def InventoryTurnoverRatio(data):
    """
    TODO: calculate INVENTORY_TURNOVER_RATIO
    存貨週轉率(%) = 營業成本(千) / 存貨(千)
    """
    try:
        if '存貨合計' in data['資產負債表']:
            Inventory = float(data['資產負債表']['存貨合計']['Value'])
        else:
            Inventory = float(data['資產負債表']['存貨']['Value'])
    except:
        Inventory = 0 
    try:
        if '營業成本合計' in data['綜合損益表'].keys():
            CostofOperation = float(data['綜合損益表']['營業成本合計']['Value'])
        else:
            CostofOperation = float(data['綜合損益表']['營業成本']['Value'])
    except:
        CostofOperation = 0
        try:
            CostofOperation += float(data['綜合損益表']['銷貨成本']['Value'])
        except:
            pass
        try:
            CostofOperation += float(data['綜合損益表']['租賃成本']['Value'])
        except:
            pass
        try:
            CostofOperation += float(data['綜合損益表']['推銷費用']['Value'])
        except:
            pass
    return CostofOperation / Inventory * 100 if Inventory else float('nan')
    
def FixedAssetTurnoverRatio(data):
    """
    TODO: calculate FIXED_ASSET_TURNOVER_RATIO
    固定資產週轉率(%) = 營業收入淨額(千) / 固定資產(千)
    """
    FixedAsset = GetFixedAsset(data)
    Revenue = GetRevenue(data)
    return Revenue / FixedAsset * 100 if FixedAsset else float('nan')

def TotalAssetTurnoverRatio(data):
    """
    TODO: calculate TOTAL_ASSET_TURNOVER_RATIO
    總資產週轉率(%) = 營業收入淨額(千) / 資產總計(千)
    """
    Revenue = GetRevenue(data)
    TotalAsset = GetTotalAsset(data)
        
    return Revenue / TotalAsset * 100 if TotalAsset else float('nan')

def NetTurnoverRatio(data):
    """
    TODO: calculate NET_TURNOVER_RATIO
    淨值週轉率(%) = 營業收入淨額(千) / 股東權益(千)
    """
    Revenue = GetRevenue(data)
    TotalRights = GetTotalRights(data)
    return Revenue / TotalRights * 100
    
def OperatingIncome2CapitalRatio(data):
    """
    TODO: calculate OPERATING_INCOME_TO_CAPITAL_RATIO 
    營運收入 / (流動資產(千) - 流動負債(千))
    """
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    Revenue = GetRevenue(data)
    return Revenue / (FlowAsset - FlowDebt) * 100
    
def PretaxProfit2CapitalRatio(data):
    """
    TODO: calculate PRETAX_PROFIT_TO_CAPITAL_RATIO 
    稅前淨利 / (流動資產(千) - 流動負債(千))
    """
    ReturnBeforeFee = float(data['現金流量表']['本期稅前淨利（淨損）']['Value'])
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    return ReturnBeforeFee / (FlowAsset + FlowDebt) * 100
    
def GrossMargin(data):
    """
    TODO: calculate GROSS_MARGIN
    毛利率(%) = 營業毛利(千) / 營業收入淨額(千)
    """
    try:
        Profit = float(data['綜合損益表']['營業毛利（毛損）淨額']['Value'])
    except:
        Profit = float(data['綜合損益表']['繼續營業單位稅前淨利（淨損）']['Value'])
    Revenue = GetRevenue(data)
    return Profit / Revenue if Revenue else float('nan')

def OperatingExpenseRatio(data):
    """
    TODO: calculate OPERATING_EXPENSE_RATIO
    營業費用率
    """
    Expense = GetExpense(data)
    Revenue = GetRevenue(data)
    return Expense / Revenue * 100 if Revenue else float('nan')
    
def OperatingProfitRatio(data):
    """
    TODO: calculate OPERATING_PROFIT_RATIO
    營業利益率(%) = 營業利益(千) / 營業收入淨額(千)
    """
    Revenue = GetRevenue(data)
    PnL = GetPnL(data)
    return PnL / Revenue * 100 if Revenue else float('nan')

def PretaxProfitMargin(data):
    """
    TODO: calculate PRETAX_PROFIT_MARGIN
    稅前純益率(%) = 稅前純益(千) / 營業收入淨額(千)
    """
    Revenue = GetRevenue(data)
    PretaxProfit = GetPretaxPnL(data)
    return PretaxProfit / Revenue  if Revenue else float('nan')

def FinalProfitMargin(data):
    """
    TODO: calculate FINAL_PROFIT_MARGIN 
    稅後純益率(%) = 稅前純益(千) / 營業收入淨額(千)
    """
    Revenue = GetRevenue(data)
    NetPnL = GetPnL(data)
    return NetPnL / Revenue  if Revenue else float('nan')

def PretaxReturnOnEquity(data):
    """
    TODO: calculate PRETAX_RETURN_ON_EQUITY
    稅前淨值報酬率(%) = 稅前純益(千) / 股東權益(千)
    """
    TotalRights = GetTotalRights(data)
    PretaxProfit = GetPretaxPnL(data)
    return PretaxProfit / TotalRights 

def AftertaxReturnOnEquity(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_EQUITY 
    稅後淨值報酬率(%) = 稅後純益(千) / 股東權益(千)
    稅後權益報酬率(ROE)
    """
    TotalRights = GetTotalRights(data)
    ReturnAfterFee = GetPnL(data)
    return ReturnAfterFee / TotalRights

def PretaxReturnOnAssets(data):
    """
    TODO: calculate PRETAX_RETURN_ON_ASSETS
    稅前資產報酬率(%) = 稅前純益(千) / 資產總計(千)
    """
    ReturnBeforeFee = GetPretaxPnL(data)
    TotalAsset = GetTotalAsset(data)
    return ReturnBeforeFee / TotalAsset

def AftertaxReturnOnAssets(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_ASSETS 
    稅後資產報酬率(%) = 稅後純益(千) / 資產總計(千)
    稅後資產報酬率(ROA)
    """
    ReturnAfterFee = GetPnL(data)
    TotalAsset = GetTotalAsset(data)
    return ReturnAfterFee / TotalAsset

def AftertaxReturnOnFixedAssets(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_FIXED_ASSETS
    本期淨利 / 非流動資產
    """
    ReturnAfterFee = GetPnL(data)
    FixedAsset = GetFixedAsset(data)
    return ReturnAfterFee / FixedAsset

def RevenueQuarterlyChangeRatio(last_data, update_data):
    """
    TODO: calculate REVENUE_QUARTERLY_CHANGE_RATIO 
    營業收入變化率(季)
    """
    LastRevenue = GetRevenue(last_data)
    CurrentRevenue = GetRevenue(update_data)
    return (CurrentRevenue / LastRevenue - 1) * 100

def RevenueGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate REVENUE_GROWTH_RATIO
    營收成長率(%) = (營業收入淨額(千) - 去年同期營業收入淨額(千)) / 去年同期營業收入淨額(千)
    """
    LastRevenue = GetRevenue(pre_y_data)
    CurrentRevenue = GetRevenue(update_data)
    return (CurrentRevenue / LastRevenue - 1) * 100 if LastRevenue else float('nan')

def TotalAssetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate TOTAL_ASSET_GROWTH_RATIO 
    總資產成長率(%) = (資產總計(千) - 去年同期資產總計(千)) / 去年同期資產總計(千)
    """
    LastTotalAsset = GetTotalAsset(pre_y_data)
    CurrentTotalAsset = GetTotalAsset(update_data)
    return (CurrentTotalAsset / LastTotalAsset - 1) * 100

def NetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate NET_GROWTH_RATIO
    淨值成長率(%) = (股東權益(千) - 去年同期股東權益(千)) / 去年同期股東權益(千)
    """
    LastTotalRights = GetTotalRights(pre_y_data)
    CurrentTotalRights = GetTotalRights(update_data)
    return (CurrentTotalRights / LastTotalRights - 1) * 100
    
def FixedAssetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate FIXED_ASSET_GROWTH_RATIO
    固定資產成長率(%) = (固定資產(千) - 去年同期固定資產(千)) / 去年同期固定資產(千)
    """
    
    LastFixedAsset = GetFixedAsset(pre_y_data)
    CurrentFixedAsset = GetFixedAsset(update_data)
    return (CurrentFixedAsset / LastFixedAsset - 1) * 100

def RDExpenseRatio(data):
    """
    TODO: calculate RD_EXPENSE_RATIO
    研發費用比率(%) = 研發費用(千) / 營業收入淨額(千)
    """
    Revenue = GetRevenue(data)
    try:
        if '研究發展費用合計' in data['綜合損益表'].keys():
            RD = float(data['綜合損益表']['研究發展費用合計']['Value'])
        else:
            RD = float(data['綜合損益表']['研究發展費用']['Value'])
    except:
        RD = 0
    return RD / Revenue * 100 if Revenue else float('nan')

def ManagementExpenseRatio(data):
    """
    TODO: calculate MANAGEMENT_EXPENSE_RATIO
    管銷費用比率(%) = 管銷費用(千) / 營業收入淨額(千)
    """
    Revenue = GetRevenue(data)
    try:
        if '推銷費用合計' in data['綜合損益表'].keys():
            SalesExpense = float(data['綜合損益表']['推銷費用合計']['Value'])
        else:
            SalesExpense = float(data['綜合損益表']['推銷費用']['Value'])
    except:
        SalesExpense = 0
    try:
        if '管理費用合計' in data['綜合損益表'].keys():
            ManagementExpense = float(data['綜合損益表']['管理費用合計']['Value'])
        else:
            ManagementExpense = float(data['綜合損益表']['管理費用']['Value'])
    except:
        ManagementExpense = 0
    return (SalesExpense + ManagementExpense) / Revenue * 100 if Revenue else float('nan')

def CashFlowRatio(data):
    """
    TODO: calculate CASH_FLOW_RATIO
    現金流量比率 = 營業活動的淨現金流量／流動負債
    營業活動的淨現金流量 = 本期稅後淨利 +/- 不影響現金流量之收益費損(折舊費用、攤銷費用..) +/-  營業活動相關之資產及負債淨變動(應收帳款、存貨增減、預付款項..)＋收取之利息＋收取之股利- 支付之利息 .
    """
    ReturnAfterFee = GetPnL(data)
    FlowDebt = GetTotalFlowDebt(data)
    return ReturnAfterFee / FlowDebt * 100 if FlowDebt else float('nan')

def BusinessGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate BUSINESS_GROWTH_RATIO 
    營業利益成長率 = Pre營業利益（損失） / Last營業利益（損失） - 1
    """
    PreBusinessPnL = GetPnL(pre_y_data)
    LastBusinessPnL = GetPnL(update_data)
    return (LastBusinessPnL / PreBusinessPnL - 1) * 100

def PretaxNetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate PRETAX_NET_GROWTH_RATIO
    稅前淨利成長率
    """
    LastReturnBeforeFee = GetPretaxPnL(pre_y_data)
    CurrentReturnBeforeFee = GetPretaxPnL(update_data)
    return (CurrentReturnBeforeFee / LastReturnBeforeFee - 1) * 100

def AftertaxNetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate AFTERTAX_NET_GROWTH_RATIO
    稅後淨利成長率
    """
    try:
        LastReturnAfterFee = float(pre_y_data['綜合損益表']['本期淨利（淨損）']['Value'])
        CurrentReturnAfterFee = float(update_data['綜合損益表']['本期淨利（淨損）']['Value'])
    except:
        return BusinessGrowthRatio(pre_y_data, update_data) * 100
    else:
        return (CurrentReturnAfterFee / LastReturnAfterFee - 1) * 100

def FinanceCreditEvaluation(data):
    """
    TODO: calculate FINANCE_CREDIT_EVALUATION
    財務信用評估
    1. (FFO)營運現金流 = 稅後淨利 ± 與現金無關的損益科目(例如折舊、攤提、投資收益) ± 營運資金項目的變動(例如應收帳款、存貨、應付帳款)
    2. (Debt)資產負債率 =（負債總額 ÷ 資產總額）
    3. (EBITDA) = Earning before extraordinary items + Income taxes + Interest + Amortization (稅前息前利潤+折舊與攤銷)
    4. (CFO)
    5. FOCF=EBIT(1-TAX)+ DEP. - △WCR - Capex
        其中 △WCR，中的WCR為營業資本需求= 營業資產-營業負債，即為 WCR= 應收賬款+ 存貨+預付賬款-(應付賬款+預提)。
    6. Interest
    """
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    Payables = float(data['資產負債表']['應付帳款合計']['Value'])
    Inventory = float(data['資產負債表']['存貨合計']['Value'])
    Reveivable = float(data['資產負債表']['應收帳款淨額']['Value'])
    PrePayment = float(data['資產負債表']['預付款項合計']['Value'])
    NetPnL = float(data['現金流量表']['本期淨利（淨損）']['Value'])
    FlowAsset = GetFlowAsset(data)
    FlowDebt = GetTotalFlowDebt(data)
    Debt = LiabilityRatio(data)

def CalculateAllIndicators(last_datas, update_datas, pre_y_datas):
    return dict(
    FIXED_ASSETS_RATIO = FixedAssetsRatio(update_datas),
    FIXED_ASSETS_EQUITY_RATIO = FixedAssetsEquityRatio(update_datas),
    FIXED_ASSETS_LONG_TERM_DEBT_RATIO = FixedAssetsLongTermDebtRatio(update_datas),
    FIXED_ASSETS_LONG_TERM_FUNDS_RATIO = FixedAssetsLongTermFundsRatio(update_datas),
    LIABILITY_RATIO = LiabilityRatio(update_datas),
    LONG_TERM_FUNDS_FIXED_ASSETS_RATIO = LongTermFundsFixedsAssetsRatio(update_datas),
    EQUITY_LIABILITY_RATIO = EquityLiabilityRatio(update_datas),
    EQUITY_LONG_TERM_DEBT_RATIO = EquityLongTermDebtRatio(update_datas),
    CAPITAL_TOTAL_ASSETS_REATIO = CapitalTotalAssetsRatio(update_datas),
    NET_RATIO = NetRatio(update_datas),
    LONG_TERM_DEBT_NET_RATIO = LongTermDebtNetRatio(update_datas),
    FIXED_ASSET_NET_RATIO = FixedAssetsNetRatio(update_datas),
    LEVERAGE_RATIO = LeverageRatio(update_datas),
    CURRENT_RATIO = CurrentRatio(update_datas),
    QUICK_RATIO = QuickRatio(update_datas),
    CASH_TO_CURRENT_ASSETS_RATIO = Cash2CurrentAssetsRatio(update_datas),
    CASH_TO_CURRENT_LIABILITY_RATIO = Cash2CurrentLiabilityRatio(update_datas),
    CAPITAL_TO_CURRENT_ASSETS_RATIO = Capital2CurrentDFlowDebtsRatio(update_datas),
    SHORT_TERM_BORROWING_TO_CURRENT_ASSETS_RATIO = ShortTermBorrowing2CurrentAssetsRatio(update_datas),
    PAYABLES_TURNOVER_RATIO = PayablesTurnoverRatio(last_datas, update_datas),
    REVEIVABLE_TURNOVER_RATIO = ReceivableTurnoverRatio(update_datas),
    INVENTORY_TURNOVER_RATIO = InventoryTurnoverRatio(update_datas),
    FIXED_ASSET_TURNOVER_RATIO = FixedAssetTurnoverRatio(update_datas),
    TOTAL_ASSET_TURNOVER_RATIO = TotalAssetTurnoverRatio(update_datas),
    NET_TURNOVER_RATIO = NetTurnoverRatio(update_datas),
    OPERATING_INCOME_TO_CAPITAL_RATIO = OperatingIncome2CapitalRatio(update_datas),
    PRETAX_PROFIT_TO_CAPITAL_RATIO = PretaxProfit2CapitalRatio(update_datas),
    GROSS_MARGIN = GrossMargin(update_datas),
    OPERATING_EXPENSE_RATIO = OperatingExpenseRatio(update_datas),
    OPERATING_PROFIT_RATIO = OperatingProfitRatio(update_datas),
    PRETAX_PROFIT_MARGIN = PretaxProfitMargin(update_datas),
    FINAL_PROFIT_MARGIN = FinalProfitMargin(update_datas),
    PRETAX_RETURN_ON_EQUITY = PretaxReturnOnEquity(update_datas),
    AFTERTAX_RETURN_ON_EQUITY = AftertaxReturnOnEquity(update_datas),
    PRETAX_RETURN_ON_ASSETS = PretaxReturnOnAssets(update_datas),
    AFTERTAX_RETURN_ON_ASSETS = AftertaxReturnOnAssets(update_datas),
    AFTERTAX_RETURN_ON_FIXED_ASSETS = AftertaxReturnOnFixedAssets(update_datas),
    REVENUE_QUARTERLY_CHANGE_RATIO = RevenueQuarterlyChangeRatio(last_datas, update_datas),
    REVENUE_GROWTH_RATIO = RevenueGrowthRatio(pre_y_datas, update_datas),
    TOTAL_ASSET_GROWTH_RATIO = TotalAssetGrowthRatio(pre_y_datas, update_datas),
    NET_GROWTH_RATIO = NetGrowthRatio(pre_y_datas, update_datas),
    FIXED_ASSET_GROWTH_RATIO = FixedAssetGrowthRatio(pre_y_datas, update_datas),
    RD_EXPENSE_RATIO = RDExpenseRatio(update_datas),
    MANAGEMENT_EXPENSE_RATIO = ManagementExpenseRatio(update_datas),
    CASH_FLOW_RATIO = CashFlowRatio(update_datas),
    BUSINESS_GROWTH_RATIO = BusinessGrowthRatio(pre_y_datas, update_datas),
    PRETAX_NET_GROWTH_RATIO = PretaxNetGrowthRatio(pre_y_datas, update_datas),
    AFTERTAX_NET_GROWTH_RATIO = AftertaxNetGrowthRatio(pre_y_datas, update_datas),
    FINANCE_CREDIT_EVALUATION = float('nan') # FinanceCreditEvaluation(update_datas),
    )
    
def CalculateNullIndicators():
    return dict(
    FIXED_ASSETS_RATIO = float('nan'),
    FIXED_ASSETS_EQUITY_RATIO = float('nan'),
    FIXED_ASSETS_LONG_TERM_DEBT_RATIO = float('nan'),
    FIXED_ASSETS_LONG_TERM_FUNDS_RATIO = float('nan'),
    LIABILITY_RATIO = float('nan'),
    LONG_TERM_FUNDS_FIXED_ASSETS_RATIO = float('nan'),
    EQUITY_LIABILITY_RATIO = float('nan'),
    EQUITY_LONG_TERM_DEBT_RATIO = float('nan'),
    CAPITAL_TOTAL_ASSETS_REATIO = float('nan'),
    NET_RATIO = float('nan'),
    LONG_TERM_DEBT_NET_RATIO = float('nan'),
    FIXED_ASSET_NET_RATIO = float('nan'),
    LEVERAGE_RATIO = float('nan'),
    CURRENT_RATIO = float('nan'),
    QUICK_RATIO = float('nan'),
    CASH_TO_CURRENT_ASSETS_RATIO = float('nan'),
    CASH_TO_CURRENT_LIABILITY_RATIO = float('nan'),
    CAPITAL_TO_CURRENT_ASSETS_RATIO = float('nan'),
    SHORT_TERM_BORROWING_TO_CURRENT_ASSETS_RATIO = float('nan'),
    PAYABLES_TURNOVER_RATIO = float('nan'),
    REVEIVABLE_TURNOVER_RATIO = float('nan'),
    INVENTORY_TURNOVER_RATIO = float('nan'),
    FIXED_ASSET_TURNOVER_RATIO = float('nan'),
    TOTAL_ASSET_TURNOVER_RATIO = float('nan'),
    NET_TURNOVER_RATIO = float('nan'),
    OPERATING_INCOME_TO_CAPITAL_RATIO = float('nan'),
    PRETAX_PROFIT_TO_CAPITAL_RATIO = float('nan'),
    GROSS_MARGIN = float('nan'),
    OPERATING_EXPENSE_RATIO = float('nan'),
    OPERATING_PROFIT_RATIO = float('nan'),
    PRETAX_PROFIT_MARGIN = float('nan'),
    FINAL_PROFIT_MARGIN = float('nan'),
    PRETAX_RETURN_ON_EQUITY = float('nan'),
    AFTERTAX_RETURN_ON_EQUITY = float('nan'),
    PRETAX_RETURN_ON_ASSETS = float('nan'),
    AFTERTAX_RETURN_ON_ASSETS = float('nan'),
    AFTERTAX_RETURN_ON_FIXED_ASSETS = float('nan'),
    REVENUE_QUARTERLY_CHANGE_RATIO = float('nan'),
    REVENUE_GROWTH_RATIO = float('nan'),
    TOTAL_ASSET_GROWTH_RATIO = float('nan'),
    NET_GROWTH_RATIO = float('nan'),
    FIXED_ASSET_GROWTH_RATIO = float('nan'),
    RD_EXPENSE_RATIO = float('nan'),
    MANAGEMENT_EXPENSE_RATIO = float('nan'),
    CASH_FLOW_RATIO = float('nan'),
    BUSINESS_GROWTH_RATIO = float('nan'),
    PRETAX_NET_GROWTH_RATIO = float('nan'),
    AFTERTAX_NET_GROWTH_RATIO = float('nan'),
    FINANCE_CREDIT_EVALUATION = float('nan')
    )