# Create : 2020-12-04

__updated__ = '2020-12-05 00:48:46'

from pymongo import MongoClient
from ShareHolder import main as ShareHolder

def CashYield(data):
    """
    計算現金殖利率
    現金殖利率 = 配息元 / 股價元 >= 4%
    """
    return

def DebtRatio(data):
    """
    計算負債比
    負債比 = 總負債 / 總資產
    """
    return

def GetROE(data):
    """
    計算ROE
    ROE = Return of Equity
    """
    return

def YieldFilter(data):
    """
    挑選現金殖利率 >= 4%
    """
    return

def DebtFilter(data):
    """
    挑選負債比 < 50%
    """
    return

def ROEFilter(data):
    """
    挑選ROE > 5%
    """
    return

def HolderFilter(data):
    """
    持股比率需 > 20%
    董監持股質押比例 = 董監持股質押張數 / 總股數
    """
    return


if __name__ == '__main__':
    # 董監持股比、質押比
    holders_Status = ShareHolder()