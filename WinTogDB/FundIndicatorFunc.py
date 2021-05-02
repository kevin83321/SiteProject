# Reference : http://www.cmoney.com.tw/S2_formula.asp
# Create : 2021-03-19

__updated__ = "2021-05-02 22:17:19"

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
綜合損意表
 - 營業收入淨額(營業收入合計)
 - 銷貨成本(銷貨成本合計)
 - 營業成本(營業成本合計)
 - 營業毛利(營業毛利（毛損）淨額)
 - 營業利益(營業利益（損失）)
 - 研發費用(研究發展費用合計)
 - 管銷費用(推銷費用合計 + 管理費用合計)
"""

def FixedAssetsRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_RATIO
    固定資產比率 = 固定資產/資產總計
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    TotalAsset = float(data['資產負債表']['資產總額'])
    return FixedAsset / TotalAsset

def FixedAssetsEquityRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_EQUITY_RATIO
    固定資產對股東權益比率(%) = 固定資產(千) / 股東權益(千)
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    TotalRights = float(data['資產負債表']['權益總額'])
    return FixedAsset / TotalRights

def FixedAssetsLongTermDebtRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_LONG_TERM_DEBT_RATIO
    固定資產對長期負債比率(%) = 固定資產(千) / 長期負債(千)
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    LongTermDebt = float(data['資產負債表']['非流動負債合計'])
    return FixedAsset / LongTermDebt
    

def FixedAssetsLongTermFundsRatio(data) -> float:
    """
    TODO: calculate FIXED_ASSETS_LONG_TERM_FUNDS_RATIO
    固定資產對長期資金比率(%) = 固定資產(千) / (股東權益(千) + 長期負債(千))
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    TotalRights = float(data['資產負債表']['權益總額'])
    LongTermDebt = float(data['資產負債表']['非流動負債合計'])
    return FixedAsset / (TotalRights + LongTermDebt)

def LiabilityRatio(data) -> float:
    """
    TODO: calculate LIABILITY_RATIO
    負債比率(%)	= 負債總計(千) / 資產總計(千)
    """
    TotalDebt = float(data['資產負債表']['負債總額'])
    TotalAsset = float(data['資產負債表']['資產總額'])
    return TotalDebt / TotalAsset
    

def LongTermFundsFixedsAssetsRatio(data) -> float:
    """
    TODO: calculate LONG_TERM_FUNDS_FIXED_ASSETS_RATIO
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    pass

def EquityLiabilityRatio(data):
    """
    TODO: calculate EQUITY_LIABILITY_RATIO
    股東權益對負債比率(%) = 股東權益(千) / 負債總計(千)
    """
    TotalRights = float(data['資產負債表']['權益總額'])
    TotalDebt = float(data['資產負債表']['負債總額'])
    return TotalRights / TotalDebt

def EquityLongTermDebtRatio(data):
    """
    TODO: calculate EQUITY_LONG_TERM_DEBT_RATIO
    股東權益對長期負債比率(%) = 股東權益(千) / 長期負債(千)
    """
    TotalRights = float(data['資產負債表']['權益總額'])
    LongTermDebt = float(data['資產負債表']['非流動負債合計'])
    return TotalRights / LongTermDebt

def CapitalTotalAssetsRatio(data):
    """
    TODO: calculate CAPITAL_TOTAL_ASSETS_REATIO
    運用資本對資產總額比率(%) = (流動資產(千) - 流動負債(千)) / 資產總計(千)
    """
    TotalAsset = float(data['資產負債表']['資產總額'])
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    return (FlowAsset - FlowDebt) / TotalAsset

def NetRatio(data):
    """
    TODO: calculate NET_RATIO
    淨值比率 = 股東權益(千) / 資產總計(千)
    """
    TotalRights = float(data['資產負債表']['權益總額'])
    TotalAsset = float(data['資產負債表']['資產總額'])
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
    TotalDebt = float(data['資產負債表']['負債總額'])
    TotalRights = float(data['資產負債表']['權益總額'])
    return TotalDebt / TotalRights

def CurrentRatio(data):
    """
    TODO: calculate CURRENT_RATIO
    流動比率(%) = 流動資產(千) / 流動負債(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    return FlowAsset / FlowDebt

def QuickRatio(data) -> float:
    """
    TODO: calculate QUICK_RATIO
    速動比率(%) = (流動資產(千) - 存貨(千) - 預付費用及預付款(千)) / 流動負債(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    Inventory = float(data['資產負債表']['存貨合計'])
    PrePayment = float(data['資產負債表']['預付款項合計'])
    
    return (FlowAsset - Inventory - PrePayment) / FlowDebt

def Cash2CurrentAssetsRatio(data) -> float:
    """
    TODO: calculate CASH_TO_CURRENT_ASSETS_RATIO
    現金與流動資產比率(%) = 現金及約當現金(千) / 流動資產(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    Cash = float(data['現金流量表']['期末現金及約當現金餘額'])
    return Cash / FlowAsset

def Cash2CurrentLiabilityRatio(data) -> float:
    """
    TODO: calculate CASH_TO_CURRENT_LIABILITY_RATIO
    現金與流動負債比率(%) = 現金及約當現金(千) / 流動負債(千)
    """
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    Cash = float(data['現金流量表']['期末現金及約當現金餘額'])
    return Cash / FlowDebt

def Capital2CurrentDFlowDebtsRatio(data) -> float:
    """
    TODO: calculate CAPITAL_TO_CURRENT_ASSETS_RATIO
    運用資本與流動資產比率(%) = (流動資產(千) - 流動負債(千)) / 流動資產(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    return (FlowAsset - FlowDebt) / FlowAsset
    

def ShortTermBorrowing2CurrentAssetsRatio(data):
    """
    TODO: calculate SHORT_TERM_BORROWING_TO_CURRENT_ASSETS_RATIO
    短期借款與流動資產比率(%) = 短期借款(千) / 流動資產(千)
    """
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    ShortDebt = float(data['資產負債表']['短期借款合計'])
    return ShortDebt / FlowAsset

def PayablesTurnoverRatio(data):
    """
    TODO: calculate PAYABLES_TURNOVER_RATIO
    應付款項週轉率(%) = 銷貨成本 / 平均應付帳款
    """
    Payables = float(data['資產負債表']['應付帳款合計'])
    CostofSales = float(data['綜合損意表']['銷貨成本合計'])
    return CostofSales / Payables

def ReceivableTurnoverRatio(data):
    """
    TODO: calculate REVEIVABLE_TURNOVER_RATIO
    應收款項週轉率(%) = 營業收入淨額(千) / 應收帳款與票據(千)
    // 應收款項週轉天數 = 360 / (營業收入淨額(千) / 應收帳款與票據(千))
    """
    Reveivable = float(data['資產負債表']['應收帳款淨額'])
    Revenue = float(data['綜合損意表']['營業收入合計'])
    return Revenue / Reveivable

def InventoryTurnoverRatio(data):
    """
    TODO: calculate INVENTORY_TURNOVER_RATIO
    存貨週轉率(%) = 營業成本(千) / 存貨(千)
    """
    Inventory = float(data['資產負債表']['存貨合計'])
    CostofOperation = float(data['資產負債表']['營業成本合計'])
    return CostofOperation / Inventory
    
def FixedAssetTurnoverRatio(data):
    """
    TODO: calculate FIXED_ASSET_TURNOVER_RATIO
    固定資產週轉率(%) = 營業收入淨額(千) / 固定資產(千)
    """
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    Revenue = float(data['綜合損意表']['營業收入合計'])
    return Revenue / FixedAsset

def TotalAssetTurnoverRatio(data):
    """
    TODO: calculate TOTAL_ASSET_TURNOVER_RATIO
    總資產週轉率(%) = 營業收入淨額(千) / 資產總計(千)
    """
    Revenue = float(data['綜合損意表']['營業收入合計'])
    TotalAsset = float(data['資產負債表']['資產總額'])
    return Revenue / TotalAsset

def NetTurnoverRatio(data):
    """
    TODO: calculate NET_TURNOVER_RATIO
    淨值週轉率(%) = 營業收入淨額(千) / 股東權益(千)
    """
    Revenue = float(data['綜合損意表']['營業收入合計'])
    TotalRights = float(data['資產負債表']['權益總額'])
    return Revenue / TotalRights
    
def OperatingIncome2CapitalRatio(data):
    """
    TODO: calculate OPERATING_INCOME_TO_CAPITAL_RATIO 
    營運收入 / (流動資產(千) - 流動負債(千))
    """
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    Revenue = float(data['綜合損意表']['營業收入合計'])
    return Revenue / (FlowAsset - FlowDebt)    
    
def PretaxProfit2CapitalRatio(data):
    """
    TODO: calculate PRETAX_PROFIT_TO_CAPITAL_RATIO 
    稅前淨利 / (流動資產(千) - 流動負債(千))
    """
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）'])
    FlowAsset = float(data['資產負債表']['流動資產合計'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    return ReturnBeforeFee / (FlowAsset + FlowDebt)
    
def GrossMargin(data):
    """
    TODO: calculate GROSS_MARGIN
    毛利率(%) = 營業毛利(千) / 營業收入淨額(千)
    """
    Profit = float(data['綜合損意表']['營業毛利（毛損）淨額'])
    Revenue = float(data['綜合損意表']['營業收入合計'])
    return Profit / Revenue

def OperatingExpenseRatio(data):
    """
    TODO: calculate OPERATING_EXPENSE_RATIO
    營業費用率
    """
    pass
    
def OperatingProfitRatio(data):
    """
    TODO: calculate OPERATING_PROFIT_RATIO
    營業利益率(%) = 營業利益(千) / 營業收入淨額(千)
    """
    Income = float(data['綜合損意表']['營業收入合計'])
    Revenue = float(data['綜合損意表']['營業利益（損失）'])
    return Revenue / Income

def PretaxProfitMargin(data):
    """
    TODO: calculate PRETAX_PROFIT_MARGIN
    稅後純益率(%) = 稅後純益(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損意表']['營業收入合計'])
    NetPnL = float(data['現金流量表']['本期淨利（淨損）'])
    return NetPnL / Revenue

def FinalProfitMargin(data):
    """
    TODO: calculate FINAL_PROFIT_MARGIN 
    最後獲利率
    """
    pass

def PretaxReturnOnEquity(data):
    """
    TODO: calculate PRETAX_RETURN_ON_EQUITY
    稅前淨值報酬率(%) = 稅前純益(千) / 股東權益(千)
    """
    TotalRights = float(data['資產負債表']['權益總額'])
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）'])
    return ReturnBeforeFee / TotalRights

def AftertaxReturnOnEquity(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_EQUITY 
    稅後淨值報酬率(%) = 稅後純益(千) / 股東權益(千)
    稅後權益報酬率(ROE)
    """
    TotalRights = float(data['資產負債表']['權益總額'])
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）'])
    return ReturnAfterFee / TotalRights

def PretaxReturnOnAssets(data):
    """
    TODO: calculate PRETAX_RETURN_ON_ASSETS
    稅前資產報酬率(%) = 稅前純益(千) / 資產總計(千)
    """
    ReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）'])
    TotalAsset = float(data['資產負債表']['資產總額'])
    return ReturnBeforeFee / TotalAsset

def AftertaxReturnOnAssets(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_ASSETS 
    稅後資產報酬率(%) = 稅後純益(千) / 資產總計(千)
    稅後資產報酬率(ROA)
    """
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）'])
    TotalAsset = float(data['資產負債表']['資產總額'])
    return ReturnAfterFee / TotalAsset

def AftertaxReturnOnFixedAssets(data):
    """
    TODO: calculate AFTERTAX_RETURN_ON_FIXED_ASSETS
    本期淨利 / 非流動資產
    """
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）'])
    FixedAsset = float(data['資產負債表']['非流動資產合計'])
    return ReturnAfterFee / FixedAsset

def RevenueQuarterlyChangeRatio(data):
    """
    TODO: calculate REVENUE_QUARTERLY_CHANGE_RATIO 
    營業收入變化率(季)
    """
    LastRevenue = float(data['綜合損意表']['營業收入合計'])
    CurrentRevenue = float(data['綜合損意表']['營業收入合計'])
    return CurrentRevenue / LastRevenue - 1

def RevenueGrowthRatio(data):
    """
    TODO: calculate REVENUE_GROWTH_RATIO
    營收成長率(%) = (營業收入淨額(千) - 去年同期營業收入淨額(千)) / 去年同期營業收入淨額(千)
    """
    LastRevenue = float(data['綜合損意表']['營業收入合計'])
    CurrentRevenue = float(data['綜合損意表']['營業收入合計'])
    return CurrentRevenue / LastRevenue - 1

def TotalAssetGrowthRatio(data):
    """
    TODO: calculate TOTAL_ASSET_GROWTH_RATIO 
    總資產成長率(%) = (資產總計(千) - 去年同期資產總計(千)) / 去年同期資產總計(千)
    """
    LastTotalAsset = float(data['資產負債表']['資產總額'])
    CurrentTotalAsset = float(data['資產負債表']['資產總額'])
    return CurrentTotalAsset / LastTotalAsset - 1

def NetGrowthRatio(data):
    """
    TODO: calculate NET_GROWTH_RATIO
    淨值成長率(%) = (股東權益(千) - 去年同期股東權益(千)) / 去年同期股東權益(千)
    """
    LastTotalRights = float(data['資產負債表']['權益總額'])
    CurrentTotalRights = float(data['資產負債表']['權益總額'])
    return CurrentTotalRights / LastTotalRights - 1
    
def FixedAssetGrowthRatio(data):
    """
    TODO: calculate FIXED_ASSET_GROWTH_RATIO
    固定資產成長率(%) = (固定資產(千) - 去年同期固定資產(千)) / 去年同期固定資產(千)
    """
    LastFixedAsset = float(data['資產負債表']['非流動資產合計'])
    CurrentFixedAsset = float(data['資產負債表']['非流動資產合計'])
    return CurrentFixedAsset / LastFixedAsset - 1

def RDExpenseRatio(data):
    """
    TODO: calculate RD_EXPENSE_RATIO
    研發費用比率(%) = 研發費用(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損意表']['營業收入合計'])
    RD = float(data['綜合損意表']['研究發展費用合計'])
    return RD / Revenue

def ManagementExpenseRatio(data):
    """
    TODO: calculate MANAGEMENT_EXPENSE_RATIO
    管銷費用比率(%) = 管銷費用(千) / 營業收入淨額(千)
    """
    Revenue = float(data['綜合損意表']['營業收入合計'])
    SalesExpense = float(data['綜合損意表']['推銷費用合計'])
    ManagementExpense = float(data['綜合損意表']['管理費用合計'])
    return (SalesExpense + ManagementExpense) / Revenue

def CashFlowRatio(data):
    """
    TODO: calculate CASH_FLOW_RATIO
    現金流量比率 = 營業活動的淨現金流量／流動負債
    營業活動的淨現金流量 = 本期稅後淨利 +/- 不影響現金流量之收益費損(折舊費用、攤銷費用..) +/-  營業活動相關之資產及負債淨變動(應收帳款、存貨增減、預付款項..)＋收取之利息＋收取之股利- 支付之利息 .
    """
    ReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）'])
    FlowDebt = float(data['資產負債表']['流動負債合計'])
    pass

def BusinessGrowthRatio(data):
    """TODO: calculate BUSINESS_GROWTH_RATIO 
    """
    pass

def PretaxNetGrowthRatio(data):
    """
    TODO: calculate PRETAX_NET_GROWTH_RATIO
    稅前淨利成長率
    """
    LastReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）'])
    CurrentReturnBeforeFee = float(data['資產負債表']['本期稅前淨利（淨損）'])
    return CurrentReturnBeforeFee / LastReturnBeforeFee - 1

def AftertaxNetGrowthRatio(data):
    """
    TODO: calculate AFTERTAX_NET_GROWTH_RATIO
    稅後淨利成長率
    """
    LastReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）'])
    CurrentReturnAfterFee = float(data['資產負債表']['本期淨利（淨損）'])
    return CurrentReturnAfterFee / LastReturnAfterFee - 1

def FinanceCreditEvaluation(data):
    """
    TODO: calculate FINANCE_CREDIT_EVALUATION
    
    """
    pass

def CalculateAllIndicators(last_datas, update_datas, pre_y_datas):
    result = dict(
    FIXED_ASSETS_RATIO = FixedAssetsRatio(update_datas),
    FIXED_ASSETS_EQUITY_RATIO = FixedAssetsEquityRatio(update_datas),
    FIXED_ASSETS_LONG_TERM_DEBT_RATIO = FixedAssetsLongTermDebtRatio(update_datas),
    FIXED_ASSETS_LONG_TERM_FUNDS_RATIO = FixedAssetsLongTermFundsRatio(update_datas),
    LIABILITY_RATIO = LiabilityRatio(update_datas),
    # LONG_TERM_FUNDS_FIXED_ASSETS_RATIO = LongTermFundsFixedsAssetsRatio(update_datas),
    EQUITY_LIABILITY_RATIO = EquityLiabilityRatio(update_datas),
    EQUITY_LONG_TERM_DEBT_RATIO = EquityLongTermDebtRatio(update_datas),
    CAPITAL_TOTAL_ASSETS_REATIO = CapitalTotalAssetsRatio(update_datas),
    NET_RATIO = NetRatio(update_datas),
    LONG_TERM_DEBT_NET_RATIO = LongTermDebtNetRatio(update_datas),
    FIXED_ASSET_NET_RATIO = FixedAssetsNetRatio(update_data),
    LEVERAGE_RATIO = LeverageRatio(update_data),
    CURRENT_RATIO = CurrentRatio(update_data),
    QUICK_RATIO = QuickRatio(update_data),
    CASH_TO_CURRENT_ASSETS_RATIO = Cash2CurrentAssetsRatio(update_data),
    CASH_TO_CURRENT_LIABILITY_RATIO = Cash2CurrentLiabilityRatio(update_data)
    
    
    )