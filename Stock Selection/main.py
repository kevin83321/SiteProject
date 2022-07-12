
from TowerWithMACD import main as TowerWithMACD
from VolumeWithMACD import main as VolumeWithMACD
from IndexTrend2 import main as IndexTrend
from Find_DayTrade_By_Queen import main as DayTradeQueen
from Find_Day_Trade_Ray import main as DayTradeRay
from Find_Day_Trade_陳信宏 import main as DayTradeHung
from Short_Term_Trade_Warrant_Brother import main as ShortTermTrade
from Day_Trade_dental_stock import main as dental_stock
from ReversedBB import main as ReversedBB
from StrongTrend import main as StrongTrend
from WeakTrend import main as WeakTrend
from BottomV import main as BottomV
from CrossDayTrade import main as CrossDayTrade
from BreakTangled import main as BreakTangled
from MACrossSelection import main as MACrossSelection

def main():
    IndexTrend()
    # VolumeWithMACD(min_price=0, max_price=9999, num_shares=1000, shares_ratio=2)
    # TowerWithMACD(min_price=0, max_price=9999, num_shares=1000, shares_ratio=2)
    # DayTradeQueen(num_shares=1000, shares_ratio=2)
    # DayTradeRay(0,9999,5000,0)
    # DayTradeHung(40,99,10000,0)
    ShortTermTrade(min_price=0, max_price=9999, num_shares=1000, shares_ratio=2, num_dog=1)
    # dental_stock()
    ReversedBB(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5, num_dog=2)
    StrongTrend(min_price=0, max_price=9999, num_shares=1000, shares_ratio=2, num_dog=3)
    # WeakTrend(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    BottomV(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5, num_dog=4)
    # CrossDayTrade(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    # BreakTangled(min_price=0, max_price=9999, num_shares=1000, shares_ratio=1.5)
    MACrossSelection(min_price=0, max_price=9999, num_shares=100, shares_ratio=1.5, num_dog=5)
    
if __name__ == '__main__':
    main()