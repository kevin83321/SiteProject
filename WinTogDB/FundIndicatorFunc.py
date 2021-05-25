# Reference : http://www.cmoney.com.tw/S2_formula.asp
# Create : 2021-03-19

__updated__ = "2021-05-24 01:36:29"

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
 - 稅後純益(本期淨利（淨損）)
 - 支付之利息
 - 折舊費用
 - 攤銷費用
 - 利息費用
 - 利息收入
 - 其他投資活動
 - 投資活動之淨現金流入（流出）
綜合損益表
 - 營業收入淨額(營業收入合計)
 - 銷貨成本(銷貨成本合計)
 - 營業成本(營業成本合計)
 - 營業毛利(營業毛利（毛損）淨額)
 - 營業利益(營業利益（損失）)
 - 研發費用(研究發展費用合計)
 - 管銷費用(推銷費用合計 + 管理費用合計)
 - 營業費用(營業費用合計)
"""

def FixedAssetsRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_RATIO
    固定資產比率 = 固定資產/資產總計
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
    return FixedAsset / TotalAsset

def FixedAssetsEquityRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_EQUITY_RATIO
    固定資產對股東權益比率(%) = 固定資產(千) / 股東權益(千)
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    return FixedAsset / TotalRights

def FixedAssetsLongTermDebtRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_LONG_TERM_DEBT_RATIO
    固定資產對長期負債比率(%) = 固定資產(千) / 長期負債(千)
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    LongTermDebt = float(data['資產負債表']['非流動負債合計']['Value'])
    return FixedAsset / LongTermDebt
    

def FixedAssetsLongTermFundsRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_LONG_TERM_FUNDS_RATIO
    固定資產對長期資金比率(%) = 固定資產(千) / (股東權益(千) + 長期負債(千))
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    LongTermDebt = float(data['資產負債表']['非流動負債合計']['Value'])
    return FixedAsset / (TotalRights + LongTermDebt)

def LiabilityRatio(data) -> float:
    """
    TODO: calculate LIABILITY_RATIO
    負債比率(%)	= 負債總計(千) / 資產總計(千)
    """
    if "負債總額" not in data['資產負債表'].keys():
        TotalDebt = float(data['資產負債表']['非流動負債合計']['Value'])
        TotalDebt += float(data['資產負債表']['流動負債合計']['Value'])
    else:
        TotalDebt = float(data['資產負債表']['負債總額']['Value'])
    
    
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
    return TotalDebt / TotalAsset
    

def LongTermFundsFixedsAssetsRatio(data) -> float:
    """
    TODO: calculate LONG_TERM_FUNDS_FIXED_ASSETS_RATIO
    長期資金佔固定資產比率 = (股東權益(千) + 長期負債(千)) / 固定資產(千)
    """
    return 1 / FixedAssetsLongTermFundsRatio(data)

def EquityLiabilityRatio(data):
    """
    TODO: calculate EQUITY_LIABILITY_RATIO
    股東權益對負債比率(%) = 股東權益(千) / 負債總計(千)
    """
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    if "負債總額" not in data['資產負債表'].keys():
        TotalDebt = float(data['資產負債表']['非流動負債合計']['Value'])
        TotalDebt += float(data['資產負債表']['流動負債合計']['Value'])
    else:
        TotalDebt = float(data['資產負債表']['負債總額']['Value'])
    return TotalRights / TotalDebt

def EquityLongTermDebtRatio(data):
    """
    TODO: calculate EQUITY_LONG_TERM_DEBT_RATIO
    股東權益對長期負債比率(%) = 股東權益(千) / 長期負債(千)
    """
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    LongTermDebt = float(data['資產負債表']['非流動負債合計']['Value'])
    return TotalRights / LongTermDebt

def CapitalTotalAssetsRatio(data):
    """
    TODO: calculate CAPITAL_TOTAL_ASSETS_REATIO
    運用資本對資產總額比率(%) = (流動資產(千) - 流動負債(千)) / 資產總計(千)
    """
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
        
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    return (FlowAsset - FlowDebt) / TotalAsset

def NetRatio(data):
    """
    TODO: calculate NET_RATIO
    淨值比率 = 股東權益(千) / 資產總計(千)
    """
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
    
    return TotalRights / TotalAsset

def LongTermDebtNetRatio(data):
    """
    TODO: calculate LONG_TERM_DET_NET_RATIO
    長期負債對淨值比率(%) = 長期負債(千) / 股東權益(千)
    """
    return 1 / EquityLongTermDebtRatio(data)

def FixedAssetsNetRatio(data):
    """
    TODO: calculate FIXED_ASSETS_NET_RATIO
    固定資產對淨值比率(%) = 固定資產(千) / 股東權益(千)
    """
    return FixedAssetsRatio(data)

def LeverageRatio(data):
    """
    TODO: calculate LEVERAGE_RATIO
    槓桿比率(%) = 負債總計(千) / 股東權益(千)
    """
    if "負債總額" not in data['資產負債表'].keys():
        TotalDebt = float(data['資產負債表']['非流動負債合計']['Value'])
        TotalDebt += float(data['資產負債表']['流動負債合計']['Value'])
    else:
        TotalDebt = float(data['資產負債表']['負債總額']['Value'])
        
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    return TotalDebt / TotalRights

def CurrentRatio(data):
    """
    TODO: calculate CURRENT_RATIO
    流動比率(%) = 流動資產(千) / 流動負債(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    return FlowAsset / FlowDebt

def QuickRatio(data) -> float:
    """
    TODO: calculate QUICK_RATIO
    速動比率(%) = (流動資產(千) - 存貨(千) - 預付費用及預付款(千)) / 流動負債(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    if '存貨合計' in data['資產負債表']:
        Inventory = float(data['資產負債表']['存貨合計']['Value'])
    else:
        Inventory = float(data['資產負債表']['存貨']['Value'])
        
    if '預付款項合計' in data['資產負債表']:
        PrePayment = float(data['資產負債表']['預付款項合計']['Value'])
    else:
        PrePayment = float(data['資產負債表']['預付款項']['Value'])
    
    return (FlowAsset - Inventory - PrePayment) / FlowDebt

def Cash2CurrentAssetsRatio(data) -> float:
    """
    TODO: calculate CASH_TO_CURRENT_ASSETS_RATIO
    現金與流動資產比率(%) = 現金及約當現金(千) / 流動資產(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    Cash = float(data['現金流量表']['期末現金及約當現金餘額']['Value'])
    return Cash / FlowAsset

def Cash2CurrentLiabilityRatio(data) -> float:
    """
    TODO: calculate CASH_TO_CURRENT_LIABILITY_RATIO
    現金與流動負債比率(%) = 現金及約當現金(千) / 流動負債(千)
    """
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    Cash = float(data['現金流量表']['期末現金及約當現金餘額']['Value'])
    return Cash / FlowDebt

def Capital2CurrentDFlowDebtsRatio(data) -> float:
    """
    TODO: calculate CAPITAL_TO_CURRENT_ASSETS_RATIO
    運用資本與流動資產比率(%) = (流動資產(千) - 流動負債(千)) / 流動資產(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    return (FlowAsset - FlowDebt) / FlowAsset
    

def ShortTermBorrowing2CurrentAssetsRatio(data):
    """
    TODO: calculate SHORT_TERM_BORROWING_TO_CURRENT_ASSETS_RATIO
    短期借款與流動資產比率(%) = 短期借款(千) / 流動資產(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    
    if '短期借款合計' in data['資產負債表'].keys():
        ShortDebt = float(data['資產負債表']['短期借款合計']['Value'])
    else:
        ShortDebt = float(data['資產負債表']['短期借款']['Value'])
    
    return ShortDebt / FlowAsset

def PayablesTurnoverRatio(data):
    """
    TODO: calculate PAYABLES_TURNOVER_RATIO
    應付款項週轉率(%) = 銷貨成本 / 平均應付帳款
    """
    if '應付帳款合計' in data['資產負債表'].keys():
        Payables = float(data['資產負債表']['應付帳款合計']['Value'])
    else:
        Payables = float(data['資產負債表']['應付帳款']['Value'])
        
    if '銷貨成本合計' in data['綜合損益表'].keys():
        CostofSales = float(data['綜合損益表']['銷貨成本合計']['Value'])
    else:
        CostofSales = float(data['綜合損益表']['銷貨成本']['Value'])
    return CostofSales / Payables

def ReceivableTurnoverRatio(data):
    """
    TODO: calculate REVEIVABLE_TURNOVER_RATIO
    應收款項週轉率(%) = 營業收入淨額(千) / 應收帳款與票據(千)
    // 應收款項週轉天數 = 360 / (營業收入淨額(千) / 應收帳款與票據(千))
    """
    Reveivable = float(data['資產負債表']['應收帳款淨額']['Value'])
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    return Revenue / Reveivable

def InventoryTurnoverRatio(data):
    """
    TODO: calculate INVENTORY_TURNOVER_RATIO
    存貨週轉率(%) = 營業成本(千) / 存貨(千)
    """
    Inventory = float(data['資產負債表']['存貨合計']['Value'])
    CostofOperation = float(data['資產負債表']['營業成本合計']['Value'])
    return CostofOperation / Inventory
    
def FixedAssetTurnoverRatio(data):
    """
    TODO: calculate FIXED_ASSET_TURNOVER_RATIO
    固定資產週轉率(%) = 營業收入淨額(千) / 固定資產(千)
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    return Revenue / FixedAsset

def TotalAssetTurnoverRatio(data):
    """
    TODO: calculate TOTAL_ASSET_TURNOVER_RATIO
    總資產週轉率(%) = 營業收入淨額(千) / 資產總計(千)
    """
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
        
    return Revenue / TotalAsset

def NetTurnoverRatio(data):
    """
    TODO: calculate NET_TURNOVER_RATIO
    淨值週轉率(%) = 營業收入淨額(千) / 股東權益(千)
    """
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    return Revenue / TotalRights
    
def OperatingIncome2CapitalRatio(data):
    """
    TODO: calculate OPERATING_INCOME_TO_CAPITAL_RATIO 
    營運收入 / (流動資產(千) - 流動負債(千))
    """
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    return Revenue / (FlowAsset - FlowDebt)    
    
def PretaxProfit2CapitalRatio(data):
    """
    TODO: calculate PRETAX_PROFIT_TO_CAPITAL_RATIO 
    稅前淨利 / (流動資產(千) - 流動負債(千))
    """
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    return ReturnBeforeFee / (FlowAsset + FlowDebt)
    
def GrossMargin(data):
    """
    TODO: calculate GROSS_MARGIN
    毛利率(%) = 營業毛利(千) / 營業收入淨額(千)
    """
    Profit = float(data['綜合損益表']['營業毛利（毛損）淨額']['Value'])
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    return Profit / Revenue

def OperatingExpenseRatio(data):
    """
    TODO: calculate OPERATING_EXPENSE_RATIO
    營業費用率
    """
    Expense = float(data['綜合損益表']['營業費用合計']['Value'])
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    return Expense / Revenue
    
def OperatingProfitRatio(data):
    """
    TODO: calculate OPERATING_PROFIT_RATIO
    營業利益率(%) = 營業利益(千) / 營業收入淨額(千)
    """
    Income = float(data['綜合損益表']['營業收入合計']['Value'])
    Revenue = float(data['綜合損益表']['營業利益（損失）']['Value'])
    return Revenue / Income

def PretaxProfitMargin(data):
    """
    TODO: calculate PRETAX_PROFIT_MARGIN
    稅前純益率(%) = 稅前純益(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    PretaxProfit = float(data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    return PretaxProfit / Revenue 

def FinalProfitMargin(data):
    """
    TODO: calculate FINAL_PROFIT_MARGIN 
    稅後純益率(%) = 稅前純益(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    NetPnL = float(data['現金流量表']['本期淨利（淨損）']['Value'])
    return NetPnL / Revenue 

def PretaxReturnOnEquity(data):
    """
    TODO: calculate PRETAX_RETURN_ON_EQUITY
    稅前淨值報酬率(%) = 稅前純益(千) / 股東權益(千)
    """
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    return ReturnBeforeFee / TotalRights 

def AftertaxReturnOnEquity(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_EQUITY 
    稅後淨值報酬率(%) = 稅後純益(千) / 股東權益(千)
    稅後權益報酬率(ROE)
    """
    TotalRights = float(data['資產負債表']['權益總額']['Value'])
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）']['Value'])
    return ReturnAfterFee / TotalRights

def PretaxReturnOnAssets(data):
    """
    TODO: calculate PRETAX_RETURN_ON_ASSETS
    稅前資產報酬率(%) = 稅前純益(千) / 資產總計(千)
    """
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
        
    return ReturnBeforeFee / TotalAsset

def AftertaxReturnOnAssets(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_ASSETS 
    稅後資產報酬率(%) = 稅後純益(千) / 資產總計(千)
    稅後資產報酬率(ROA)
    """
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）']['Value'])
    
    if "資產總額" not in data['資產負債表'].keys():
        TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
        TotalAsset += float(data['資產負債表']['流動資產合計']['Value'])
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
        
    return ReturnAfterFee / TotalAsset

def AftertaxReturnOnFixedAssets(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_FIXED_ASSETS
    本期淨利 / 非流動資產
    """
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）']['Value'])
    FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    return ReturnAfterFee / FixedAsset

def RevenueQuarterlyChangeRatio(data):
    """
    TODO: calculate REVENUE_QUARTERLY_CHANGE_RATIO 
    營業收入變化率(季)
    """
    LastRevenue = float(data['綜合損益表']['營業收入合計']['Value'])
    CurrentRevenue = float(data['綜合損益表']['營業收入合計']['Value'])
    return CurrentRevenue / LastRevenue - 1

def RevenueGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate REVENUE_GROWTH_RATIO
    營收成長率(%) = (營業收入淨額(千) - 去年同期營業收入淨額(千)) / 去年同期營業收入淨額(千)
    """
    LastRevenue = float(pre_y_data['綜合損益表']['營業收入合計']['Value'])
    CurrentRevenue = float(update_data['綜合損益表']['營業收入合計']['Value'])
    return CurrentRevenue / LastRevenue - 1

def TotalAssetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate TOTAL_ASSET_GROWTH_RATIO 
    總資產成長率(%) = (資產總計(千) - 去年同期資產總計(千)) / 去年同期資產總計(千)
    """
    if "資產總額" not in pre_y_data['資產負債表'].keys():
        LastTotalAsset = float(pre_y_data['資產負債表']['非流動資產合計']['Value'])
        LastTotalAsset += float(pre_y_data['資產負債表']['流動資產合計']['Value'])
    else:
        LastTotalAsset = float(pre_y_data['資產負債表']['資產總額']['Value'])
        
    if "資產總額" not in update_data['資產負債表'].keys():
        CurrentTotalAsset = float(update_data['資產負債表']['非流動資產合計']['Value'])
        CurrentTotalAsset += float(update_data['資產負債表']['流動資產合計']['Value'])
    else:
        CurrentTotalAsset = float(update_data['資產負債表']['資產總額']['Value'])
    return CurrentTotalAsset / LastTotalAsset - 1

def NetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate NET_GROWTH_RATIO
    淨值成長率(%) = (股東權益(千) - 去年同期股東權益(千)) / 去年同期股東權益(千)
    """
    LastTotalRights = float(pre_y_data['資產負債表']['權益總額']['Value'])
    CurrentTotalRights = float(update_data['資產負債表']['權益總額']['Value'])
    return CurrentTotalRights / LastTotalRights - 1
    
def FixedAssetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate FIXED_ASSET_GROWTH_RATIO
    固定資產成長率(%) = (固定資產(千) - 去年同期固定資產(千)) / 去年同期固定資產(千)
    """
    LastFixedAsset = float(pre_y_data['資產負債表']['非流動資產合計']['Value'])
    CurrentFixedAsset = float(update_data['資產負債表']['非流動資產合計']['Value'])
    return CurrentFixedAsset / LastFixedAsset - 1

def RDExpenseRatio(data):
    """
    TODO: calculate RD_EXPENSE_RATIO
    研發費用比率(%) = 研發費用(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    RD = float(data['綜合損益表']['研究發展費用合計']['Value'])
    return RD / Revenue

def ManagementExpenseRatio(data):
    """
    TODO: calculate MANAGEMENT_EXPENSE_RATIO
    管銷費用比率(%) = 管銷費用(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    SalesExpense = float(data['綜合損益表']['推銷費用合計']['Value'])
    ManagementExpense = float(data['綜合損益表']['管理費用合計']['Value'])
    return (SalesExpense + ManagementExpense) / Revenue

def CashFlowRatio(data):
    """
    TODO: calculate CASH_FLOW_RATIO
    現金流量比率 = 營業活動的淨現金流量／流動負債
    營業活動的淨現金流量 = 本期稅後淨利 +/- 不影響現金流量之收益費損(折舊費用、攤銷費用..) +/-  營業活動相關之資產及負債淨變動(應收帳款、存貨增減、預付款項..)＋收取之利息＋收取之股利- 支付之利息 .
    """
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    pass

def BusinessGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate BUSINESS_GROWTH_RATIO 
    營業利益成長率 = Pre營業利益（損失） / Last營業利益（損失） - 1
    """
    PreBusinessPnL = float(pre_y_data['綜合損益表']['營業利益（損失）']['Value'])
    LastBusinessPnL = float(update_data['綜合損益表']['營業利益（損失）']['Value'])
    return LastBusinessPnL / PreBusinessPnL - 1

def PretaxNetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate PRETAX_NET_GROWTH_RATIO
    稅前淨利成長率
    """
    LastReturnBeforeFee = float(pre_y_data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    CurrentReturnBeforeFee = float(update_data['資產負債表']['本期稅前淨利（淨損）']['Value'])
    return CurrentReturnBeforeFee / LastReturnBeforeFee - 1

def AftertaxNetGrowthRatio(pre_y_data, update_data):
    """
    TODO: calculate AFTERTAX_NET_GROWTH_RATIO
    稅後淨利成長率
    """
    LastReturnAfterFee = float(pre_y_data['資產負債表']['本期淨利（淨損）']['Value'])
    CurrentReturnAfterFee = float(update_data['資產負債表']['本期淨利（淨損）']['Value'])
    return CurrentReturnAfterFee / LastReturnAfterFee - 1

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
    FlowAsset = float(data['資產負債表']['流動資產合計']['Value'])
    FlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
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
    PAYABLES_TURNOVER_RATIO = PayablesTurnoverRatio(update_datas),
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
    REVENUE_QUARTERLY_CHANGE_RATIO = RevenueQuarterlyChangeRatio(update_datas),
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