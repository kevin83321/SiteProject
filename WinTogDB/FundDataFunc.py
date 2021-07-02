# Reference : http://www.cmoney.com.tw/S2_formula.asp
# Create : 2021-03-19

__updated__ = "2021-06-29 01:07:07"

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
"""

def GetTotalRights(data) -> float:
    """
    取得股東權益
    """
    try:
        try:
            TotalRights = float(data['資產負債表']['權益總額']['Value'])
        except:
            TotalRights = float(data['資產負債表']['權益總計']['Value'])
    except:
        TotalRights = float(data['資產負債表']['權益']['Value'])
    return TotalRights

def GetFixedAsset(data) -> float:
    """
    取得非流動資產
    """
    FixedAsset = 0
    try:
        FixedAsset = float(data['資產負債表']['非流動資產合計']['Value'])
    except:
        FlowAsset = GetFlowAsset(data)
    TotalAsset = GetTotalAsset(data)
    if not FixedAsset:
        FixedAsset = TotalAsset - FlowAsset
    return FixedAsset
        
def GetTotalAsset(data) -> float:
    """
    取得總資產
    """
    if "資產總額" not in data['資產負債表'].keys():
        try:
            TotalAsset = float(data['資產負債表']['資產總計']['Value'])
        except:
            TotalAsset = float(data['資產負債表']['非流動資產合計']['Value'])
            TotalAsset += GetFlowAsset(data)
    else:
        TotalAsset = float(data['資產負債表']['資產總額']['Value'])
    return TotalAsset

def GetFlowAsset(data) -> float:
    """
    取得流動資產
    """
    FlowAsset = 0
    try:
        FlowAsset += float(data['資產負債表']['流動資產合計']['Value'])
    except:
        try:
            FlowAsset += float(data['資產負債表']['透過損益按公允價值衡量之金融資產合計']['Value'])
        except:
            try:
                FlowAsset += float(data['資產負債表']['透過其他綜合損益按公允價值衡量之金融資產']['Value'])
            except:
                pass
        try:
            try:
                FlowAsset += float(data['資產負債表']['避險之衍生金融資產']['Value'])
            except:
                FlowAsset += float(data['資產負債表']['避險之金融資產']['Value'])
        except:
            pass
        try:
            FlowAsset += float(data['資產負債表']['現金及約當現金合計']['Value'])
        except:
            FlowAsset += float(data['資產負債表']['現金及約當現金']['Value'])
        try:
            FlowAsset += float(data['資產負債表']['存放央行及拆借銀行同業合計']['Value'])
        except:
            try:
                FlowAsset += float(data['資產負債表']['存放央行及拆借銀行同業']['Value'])
            except:
                try:
                    FlowAsset += float(data['資產負債表']['轉存央行存款']['Value'])
                except:
                    pass
                try:
                    FlowAsset += float(data['資產負債表']['存放央行']['Value'])
                except:
                    pass
                try:
                    FlowAsset += float(data['資產負債表']['拆放銀行同業']['Value'])
                except:
                    pass
    return FlowAsset

def GetLongTermDebt(data) -> float:
    """
    取得長期負債 (非流動負債)
    
    """
    try:
        LongTermDebt = float(data['資產負債表']['非流動負債合計']['Value'])
    except:
        LongTermDebt = GetTotalDebt(data) - GetTotalFlowDebt(data)
    return LongTermDebt

def GetTotalFlowDebt(data) -> float:
    """
    取得流動負債
    
    金融業流動負債:
        - 央行及銀行同業存款合計
        - 透過損益按公允價值衡量之金融負債合計
        - 附買回票券及債券負債合計
        - 應付款項合計
        - 遞延所得稅負債合計
    """
    try:
        TotalFlowDebt = float(data['資產負債表']['流動負債合計']['Value'])
    except:
        TotalFlowDebt = 0
        try:
            TotalFlowDebt += float(data['資產負債表']['央行及銀行同業存款合計']['Value'])
        except:
            pass
        try:
            TotalFlowDebt += float(data['資產負債表']['透過損益按公允價值衡量之金融負債合計']['Value'])
        except:
            pass
        try:
            TotalFlowDebt += float(data['資產負債表']['附買回票券及債券負債合計']['Value'])
        except:
            pass
        try:
            TotalFlowDebt += float(data['資產負債表']['應付款項合計']['Value'])
        except:
            pass
        try:
            TotalFlowDebt += float(data['資產負債表']['遞延所得稅負債合計']['Value'])
        except:
            pass
    return TotalFlowDebt

def GetTotalDebt(data) -> float:
    """
    取得總負債
    """
    if "負債總額" in data['資產負債表'].keys():
        TotalDebt = float(data['資產負債表']['負債總額']['Value'])
    else:
        try:
            TotalDebt = float(data['資產負債表']['負債總計']['Value'])
        except:
            TotalDebt = float(data['資產負債表']['非流動負債合計']['Value'])
            TotalDebt += float(data['資產負債表']['流動負債合計']['Value'])
    return TotalDebt

def GetCash(data):
    """
    取得期末現金
    """
    Cash = float(data['現金流量表']['期末現金及約當現金餘額']['Value'])
    return Cash

def GetRevenue(data) -> float:
    """
    取得營業收入
    """
    try:
        Revenue = float(data['綜合損益表']['營業收入合計']['Value'])
    except:
        Revenue = float(data['現金流量表']['營業活動之淨現金流入（流出）']['Value'])
    return Revenue
    
def GetPnL(data):
    """
    取得營業利益(本期稅後淨利)
    """
    try:
        PnL = float(data['綜合損益表']['營業利益（損失）']['Value'])
    except:
        try:
            PnL = float(data['綜合損益表']['繼續營業單位本期淨利（淨損）']['Value'])
        except:
            PnL = float(data['綜合損益表']['繼續營業單位本期稅後淨利（淨損）']['Value'])
    return PnL

def GetPretaxPnL(data):
    """
    取得稅前淨利
    """
    PretaxProfit = float(data['現金流量表']['本期稅前淨利（淨損）']['Value'])
    return PretaxProfit

def GetExpense(data):
    """
    取得營業費用
    """
    try:
        Expense = float(data['綜合損益表']['營業費用合計']['Value'])
    except:
        try:
            Expense = float(data['綜合損益表']['其他營業費用合計']['Value'])
        except:
            Expense = float(data['綜合損益表']['支出及費用合計']['Value'])
    return Expense