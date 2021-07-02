
from TowerWithMACD import main as TowerWithMACD
from VolumeWithMACD import main as VolumeWithMACD
from IndexTrend import main as IndexTrend
from Find_DayTrade_By_Queen import main as DayTradeQueen
from Find_Day_Trade_Ray import main as DayTradeRay
from Find_Day_Trade_陳信宏 import main as DayTradeHung
from Short_Term_Trade_Warrant_Brother import main as ShortTermTrade
from Day_Trade_dental_stock import main as dental_stock

def main():
    IndexTrend()
    VolumeWithMACD(min_price=20, max_price=200, num_shares=2000, shares_ratio=0)
    TowerWithMACD(min_price=0, max_price=50, num_shares=0, shares_ratio=1.5)
    DayTradeQueen(num_shares=500, shares_ratio=2)
    DayTradeRay(5,30,50000,0)
    DayTradeHung(40,99,10000,0)
    ShortTermTrade()
    dental_stock()
    
if __name__ == '__main__':
    main()