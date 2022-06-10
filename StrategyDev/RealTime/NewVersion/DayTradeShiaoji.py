import shioaji as sj
from pymongo import MongoClient
from datetime import datetime, timedelta
from pandas import DataFrame
import numpy as np
from Messenger.LineMessenger import LineMessenger as Line
from time import sleep
from shioaji import TickSTKv1, Exchange, BidAskSTKv1, TickFOPv1, BidAskFOPv1
from prettytable import PrettyTable

import warnings
warnings.filterwarnings("ignore")

import json
import os 
parent = os.path.dirname(os.path.abspath("__file__"))
StrongPath = os.path.join(parent, 'StrongTickers')
if not os.path.isdir(StrongPath):
    os.makedirs(StrongPath)

setting = {
    'user':'kevin83321',
    'pwd':'j7629864',
    'ip':'192.168.2.173',
    'port':'49153'
}

NotifyTickers = {}

def get_minimum_tick(cost):
    if cost < 10:
        return 0.01
    elif cost < 50:
        return 0.05
    elif cost < 100:
        return 0.1
    elif cost < 500:
        return 0.5
    elif cost < 1000:
        return 1
    else:
        return 5
    
def get_commission(price:float, multiplier:int=1000, qty=1, Real:bool=True, direction:str='', dayTrade:bool=False):
    """
    計算個別部位的單邊交易成本

    Params:
        symbol : 商品代碼
        exchange : 交易所
        cost : 交易價格
        multiplier : 價格還原現金之乘數
            例如:
                股票 : 1張 = 1,000股，10元的股票還原現金價值，即為10 *1,000 = 10,000元
                期貨 : 台指期1點200元，假設現在10,000點，則一口台股的價值為 200 * 10,000 = 2,000,000
        qty : 買賣口數或張數
        Real : 是否為實單, default = False
        direction : 交易方向 進場(買賣)或出場
            P.S. 股票交易的交易稅是出場才計算
    """
    tick = get_minimum_tick(price)
    commission = price * (0.1425 / 100) * multiplier * qty
    commission = 20 if commission < 20 else commission
    fee = price * (0.3 / 100) * multiplier * qty
    if dayTrade:
        fee /= 2
    slide = tick * multiplier
    tradeCost = commission * 0.6
    if direction == 'EXIT' or direction == 0:
        tradeCost += fee
    if not Real:
        tradeCost += slide * qty
    return tradeCost

def readStrongTicker(dtStr):
    if os.path.isfile(os.path.join(StrongPath, f'{dtStr}_strongTicker.json')):
        with open(os.path.join(StrongPath, f'{dtStr}_strongTicker.json'), 'r') as f:
            tickers = json.load(f)
            return tickers
    else:
        return {}

def quote_callback(exchange:Exchange, tick):
    # [TickSTKv1, BidAskSTKv1, TickFOPv1, BidAskFOPv1]
    global NotifyTickers
    try:
        NotifyTickers[tick.code] = NotifyTickers.get(tick.code, 
                                                     DataObject(tmp_contract, open_threshold=open_thresholds[tick.code], 
                                                                api=api1, max_size = max_size_map[tick.code]))
        if type(tick) in [TickSTKv1, TickFOPv1]:
            NotifyTickers[tick.code].updateQ20Dict(dict(
                symbol=tick.code,
                datetime=tick.datetime,
                open=float(tick.open),
                high=float(tick.high),
                low=float(tick.low),
                close=float(tick.close),
                avg_price=float(tick.avg_price),
                qty=int(tick.volume),
                totalQty=int(tick.total_volume),
                pct_chg=float(tick.pct_chg),
                simulate=bool(tick.simtrade),
            ))
#             print(f"Exchange : {exchange}, Tick:{NotifyTickers[ticker].q20_data}\n")
        if type(tick) in [BidAskSTKv1, BidAskFOPv1]:
            NotifyTickers[tick.code].updateQ80Dict(dict(
                symbol = tick.code,
                datetime = tick.datetime,
                bid1 = float(tick.bid_price[0]),
                bid2 = float(tick.bid_price[1]),
                bid3 = float(tick.bid_price[2]),
                bid4 = float(tick.bid_price[3]),
                bid5 = float(tick.bid_price[4]),
                bidQty1 = float(tick.bid_volume[0]),
                bidQty2 = float(tick.bid_volume[1]),
                bidQty3 = float(tick.bid_volume[2]),
                bidQty4 = float(tick.bid_volume[3]),
                bidQty5 = float(tick.bid_volume[4]),
                askQty1 = float(tick.ask_volume[0]),
                askQty2 = float(tick.ask_volume[1]),
                askQty3 = float(tick.ask_volume[2]),
                askQty4 = float(tick.ask_volume[3]),
                askQty5 = float(tick.ask_volume[4]),
                ask1 = float(tick.ask_price[0]),
                ask2 = float(tick.ask_price[1]),
                ask3 = float(tick.ask_price[2]),
                ask4 = float(tick.ask_price[3]),
                ask5 = float(tick.ask_price[4]),
            ))
            # print(f"Exchange : {exchange}, BidAsk : {NotifyTickers[ticker].q80_data}\n")
    except Exception as e:
        print(e)

def place_cb(stat, msg):
    print('my_place_callback')
    print(stat, msg)

def createSummaryTable(tickers, pnl_list:list=None, max_pnl_list:list=None, max_size_list:list=None, ret_list:list=None):
    try:
        table = PrettyTable()
        table.add_column('代號', tickers)
        table.add_column("損益", pnl_list)
        table.add_column("報酬率", ret_list)
        table.add_column("最大倉位", max_size_list)
        table.add_column("最大倉損益", max_pnl_list)
        table.align = 'r'
    except Exception as e:
        print(e)
    else:
        return table

class DataObject:
    
    opening = False
    closing = False
    
    name:str=""
    pre_time:str="09:00:00"
    pre_volume:int = 0
    pre_close:int = 0
    total_v:int = 0
    q20_data:dict = {}
    q80_data:dict = {} 
    open_threshold:float = 0
    _api = None
    symbol:str = ""
    refPrice:float = 0
    entry_percent:float = .06
    exit_percent:float = .09
    sl_ratio:float = .03
    v_threshold:float = .01
    entry_threshold:float = 0
    exit_threshold:float = 0
    max_ret:float = 0
    tmp_ret:float = 0
    pos = 0
    traded = 0
    entry = 0
    entry_time = 0
    order = None
    onOrderProcess = False

    preHigh = None
    preLow = None
    
    pnl:float = 0
    
    def __init__(self, contract, open_threshold:float, api=None, PreData:dict=None,
                 v_threshold:float=.01, entry_percent:float=.06, exit_percent:float=.09, 
                 takeprofit:float=.6, start_moving_take = .015, sl_ratio:float=.03, max_size:float = 1):
        self.contract = contract
        self.open_threshold = open_threshold
        self.entry_percent = entry_percent
        self.exit_percent = exit_percent
        self.takeprofit = takeprofit
        self.start_moving_take = start_moving_take
        self.sl_ratio = sl_ratio
        self.v_threshold = v_threshold
        self._initialByContract(contract)
        self.max_size = max_size
        self._api = api
        self.first_5mink = {'open':None, 'high':0,'low':9999, 'close':0}
        if PreData:
            self.preHigh = PreData['PreHigh']
            self.preLow = PreData['PreLow']
        
    def _initialByContract(self, contract):
        self.symbol = contract.code
        self.refPrice = contract.reference
        self.entry_threshold = self.refPrice * (1 + self.entry_percent)
        self.exit_threshold = self.refPrice * (1 + self.exit_percent)
        self.name = contract.name
        
    def updateQ20Dict(self, data:dict={}):

        if data is None:return
        if data['simulate'] :return
        if data['symbol'] != self.symbol: return
        self.q20_data = data
        self.q20_data['timeStr'] = self.q20_data['datetime'].strftime("%H:%M:%S")
        self.updateSignal()
        self.updateStatus()
    
    def updateQ80Dict(self, data:dict):

        if data['symbol'] != self.symbol: return
        self.q80_data = data
    
    def updateOrderDeal(self, data):
        if type(data) == sj.constant.OrderState.TFTOrder:
            onOrderProcess = True
        elif type(data) == sj.constant.OrderState.TFTDeal:
            self.pos += (1 if data['action'] == sj.constant.Action.Buy else -1) * data['quantity']
            self.entry = data['price']
            # if self.pos == 0:
            #     self.traded = True
    
    def updateStatus(self):
        """
        Chech position profit loss
        """
        if not self.pos: return
        if self.traded: return
        if self.closing or self.opening: return
        close = self.q20_data['close']
        tmp_pnl = (close - self.entry) * 1000 * self.pos
        tmp_pnl -= int(get_commission(self.entry if self.pos > 0 else close)) # 進場成本
        tmp_pnl -= int(get_commission(close if self.pos > 0 else self.entry, direction='EXIT', dayTrade=True)) # 出場成本
        tmp_ret = tmp_pnl / (self.entry * 1000)
        self.tmp_ret = ((close / self.entry) - 1) * self.pos
        self.max_ret = max(self.max_ret, self.tmp_ret)
        # print(self.symbol, self.tmp_ret, self.max_ret, close, self.pos)
        
        do_exit_take = False
        if self.max_ret >= self.start_moving_take:
            do_exit_take = (self.tmp_ret / self.max_ret) <= (self.takeprofit) if self.max_ret else False
        do_exit_stop = self.tmp_ret <= -self.sl_ratio
        do_exit = close >= self.exit_threshold if self.pos > 0 else close <= (self.refPrice * (1 - self.exit_percent))
        exit_end = self.q20_data['timeStr'] >= '13:20:00:000000'
        if any([do_exit, do_exit_take, do_exit_stop, exit_end]):
            self.closing=True
            self.DoTrade('S' if self.pos > 0 else 'B')
            self.sendNotifyExit(self.q20_data['datetime'].strftime("%H:%M:%S.%f"), self.symbol, self.name,
                             close, self.q20_data['pct_chg'], do_exit_take or do_exit)
    
    def updateSignal(self):
        # print("updateSignal")
        if not self.q20_data : return
        if self.order: return
        if self.pos: return
        if self.traded: return
        totalV = self.q20_data['totalQty']
        close = self.q20_data['close']
        volume = self.q20_data['qty']
        if self.q20_data['timeStr'] != self.pre_time:
            self.total_v = volume
            self.pre_time = self.q20_data['timeStr']
            self.pre_volume = totalV
        else:
            self.total_v += volume
        if not self.pre_close: 
            self.pre_close = close
            if self.first_5mink['open'] is None:
                self.first_5mink['open'] = close
            self.first_5mink['high'] = max(self.first_5mink['high'], close)
            self.first_5mink['low'] = min(self.first_5mink['low'], close)
            self.first_5mink['close'] = close
            self.pre_volume = totalV
            # print(self.symbol, self.first_5mink)
            return
        
        # print(self.symbol, self.first_5mink, close)
        v_ratio = self.total_v / self.pre_volume
        self.pre_volume = totalV
        if self.q20_data['timeStr'] < '09:05:00:000000':
            self.first_5mink['high'] = max(self.first_5mink['high'], close)
            self.first_5mink['low'] = min(self.first_5mink['low'], close)
            self.first_5mink['close'] = close
        
        else: 
            if all([not self.closing, not self.opening]):
                sig = 0
                if close >= max(self.first_5mink['high'], self.preHigh if self.preHigh else 0) * 1.005:
                    sig = 1
                # elif close <= min(self.first_5mink['low'], self.preLow if self.preLow else 9999) * .99:
                #     sig = -1
                if sig and not self.opening:
                    self.opening = True
                    self.DoTrade('B' if sig > 0 else 'S')
                    self.sendNotify(self.q20_data['datetime'].strftime("%H:%M:%S.%f"), self.symbol, self.name,
                                 close, self.q20_data['pct_chg'], 'B' if sig > 0 else 'S')
                
        self.pre_close = close
        
        
    def DoTrade(self, side):
        # if not self._api:return
        # order = self._api.Order(
        #     price=self.q80_data['ask1'] if side == 'B' else self.q80_data['bid1'],
        #     quantity=1,
        #     action=sj.constant.Action.Buy if side == 'B' else sj.constant.Action.Sell,
        #     price_type=sj.constant.StockPriceType.LMT,
        #     order_type=sj.constant.TFTOrderType.ROD,
        #     first_sell=sj.constant.StockFirstSell.Yes if side == 'S' else sj.constant.StockFirstSell.No,
        # )
        # self.order = self._api.place_order(self.contract, order)
        if not any([self.opening, self.closing]):return
        if abs(self.pos) > 1: return
        self.pos += 1 if side == 'B' else -1
        signal_time = self.q20_data["datetime"].strftime("%H:%M:%S.%f")
        if self.pos == 0:
            self.traded = True
            
            close = self.q80_data['ask1'] if side == 'B' else self.q80_data['bid1']
            if not close:
                close = self.q20_data['close']
            tmp_pnl = (close - self.entry) * 1000 * (1 if side == 'S' else -1)
            tmp_pnl -= int(get_commission(self.entry if side == 'S' else close)) # 進場成本
            tmp_pnl -= int(get_commission(close if side == 'S' else self.entry, direction='EXIT', dayTrade=True)) # 出場成本
            tmp_ret = tmp_pnl / (self.entry * 1000) # - 1
            self.pnl += tmp_pnl
            
            cover_text = '\n\n---------------PnL Summary--------------\n'
            cover_text = f'時間 : {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}\n'
            cover_text += f'Exit Position of {self.contract.code}\n'
            cover_text += f'Entry : {self.entry} at {self.entry_time}\n'
            cover_text += f'Exit : {close} at {signal_time}\n'
            cover_text += f'Total PnL with Cost : {tmp_pnl}\n'
            cover_text += f'Total Ret with Cost : {round(tmp_ret * 100, 2)}%\n'
            cover_text += f'Total PnL with Cost of max size {self.max_size}: {self.max_size * tmp_pnl}\n'
            cover_text += f'Trade Value: {self.entry * 1000}\n'
            Line.sendMessage(cover_text)

            print('\n---------------PnL Summary--------------')
            print(f'Exit Position of {self.contract.code}')
            print(f'Entry : {self.entry} at {self.entry_time}')
            print(f'Exit : {close} at {signal_time}')
            print(f'Total PnL with Cost : {tmp_pnl}')
            print(f'Total Ret with Cost : {round(tmp_ret * 100, 2)}%')
            print(f'Total PnL with Cost of max size {self.max_size}: {self.max_size * tmp_pnl}\n')
            
            self.entry = 0
            self.closing = False
            return
        self.entry = self.q80_data['ask1'] if side == 'B' else self.q80_data['bid1']
        if not self.entry:
            self.entry = self.q20_data['close']
        self.entry_time = signal_time
        self.opening = False
    
    def sendNotify(self, dateStr, idx, name, 
                   close, Ret, Side="B"):#, TVRatio, EVRatio):
        try:
            text = f'時間 : {dateStr}\n'
            text += f'股票代號/名稱 : {idx}/{name}\n'
            if Side == "B":
                text += f'觸發條件 : 突破第一個5分K高點\n'
                text += f'進場方向 : 做多\n'
            else:
                text += f'觸發條件 : 突破第一個5分K低點\n'
                text += f'進場方向 : 做空\n'
            text += f'成交價 : {close}\n'
            
            
            # 漲跌幅量
            text += f'漲跌幅 : {Ret} %\n'
            # text += f'量比(總/估) {TVRatio}/{EVRatio}\n'
            # text += '其他提醒 : \n'
            
            Line.sendMessage(text)
        except Exception as e:
            print(e)

    def sendNotifyExit(self, dateStr, idx, name, 
                   close, Ret, takeprofit=False):
        try:
            text = f'時間 : {dateStr}\n'
            text += f'股票代號/名稱 : {idx}/{name}\n'
            text += f'觸發出場條件 : 若有持倉，已經達到({"停利" if takeprofit else "停損"})條件囉\n'
            text += f'成交價 : {close}\n'
            
            # 漲跌幅量
            text += f'漲跌幅 : {Ret} %\n'
            # text += f'量比(總/估) {TVRatio}/{EVRatio}\n'
            # text += '其他提醒 : \n'
            
            Line.sendMessage(text)
        except Exception as e:
            print('send Exit, Error : ' + e)

if __name__ == "__main__":
    td = datetime.today()
    open_thresholds = readStrongTicker(td.strftime('%Y-%m-%d'))
    api = sj.Shioaji()
    api.login("F128497445", "j7629864")

    # Set Quote Callback
    api.quote.set_on_tick_stk_v1_callback(quote_callback)
    api.quote.set_on_bidask_stk_v1_callback(quote_callback)
    api.quote.set_on_bidask_fop_v1_callback(quote_callback)
    api.quote.set_on_tick_fop_v1_callback(quote_callback)
    
    # Set Order Callback
    api.set_order_callback(place_cb)

    tmp_ticker_list = list(open_thresholds.keys())
    for ticker in tmp_ticker_list:
        tmp_contract = api.Contracts.Stocks[ticker]
        if tmp_contract.day_trade != sj.constant.DayTrade.No:continue
        open_thresholds.pop(ticker)
        
    # seperate capital for each ticker
    total_capital = 5e6
    seperated_capital = int(total_capital / len(open_thresholds.keys()))
    max_size_map = {}
    for k, v in open_thresholds.items():
        max_pos = int(seperated_capital / (v['PreClose'] * 1000))
        print(f'{k} 最大倉位 : {max_pos}, 昨收 : {v}')
        max_size_map[k] = max_pos

    for i in range(125):
        if i < len(open_thresholds.keys()):
            ticker = sorted(open_thresholds.keys())[i]
            # ticker = "TXFL1"
            tmp_contract = api.Contracts.Stocks[ticker]
            if tmp_contract.day_trade  == sj.constant.DayTrade.Yes:
                # print("Tradable Ticker : " + ticker)
                # tmp_contract = api1.Contracts.Futures[ticker]
                NotifyTickers[ticker] = NotifyTickers.get(ticker,
                                                        DataObject(tmp_contract, open_threshold=tmp_contract.reference, 
                                                                            api=api, max_size = max_size_map[ticker], PreData=open_thresholds[ticker]))
                api.quote.subscribe(
                    tmp_contract, 
                    quote_type = sj.constant.QuoteType.Tick, # or 'tick'
                    version = sj.constant.QuoteVersion.v1 # or 'v1'
                )
                api.quote.subscribe(
                    tmp_contract, 
                    quote_type = sj.constant.QuoteType.BidAsk, # or 'tick'
                    version = sj.constant.QuoteVersion.v1 # or 'v1'
                )
    exit_time = td.replace(hour=13, minute=25, second=0)
    while datetime.now() < exit_time:
        try:
            sleep(1)
        except:
            break

    single_pnl = 0
    max_pnl = 0
    ticker_list = []
    pnl_list = []
    max_pnl_list = []
    max_size_list = []
    ret_list = []
    est_total_value = 0
    est_single_value = 0
    for d in NotifyTickers.values():
        ticker_list.append(d.symbol)
        pnl_list.append(int(d.pnl))
        max_size_list.append(d.max_size)
        max_pnl_list.append(int(d.pnl * d.max_size))
        ret_list.append(str(round(d.tmp_ret * 100, 2)) + "%")
        est_single_value += d.open_threshold * 1000
        est_total_value += d.open_threshold * 1000 * d.max_size
        # print(d.symbol, int(d.pnl), str(round(d.tmp_ret * 100, 2)) + "%", d.max_size, int(d.pnl * d.max_size))
        single_pnl += d.pnl
        max_pnl += d.pnl * d.max_size

    ticker_list.append("合計")
    pnl_list.append(int(single_pnl))
    max_size_list.append("")
    max_pnl_list.append(max_pnl)
    ret_list.append(str(round((max_pnl / est_total_value if est_total_value else 0 ) * 100, 2)) + "%")

    sum_table = createSummaryTable(ticker_list, pnl_list, max_pnl_list, max_size_list, ret_list)
    trade_result_path = os.path.join(parent, "TradeRecord")
    if not os.path.isdir(trade_result_path):
        os.makedirs(trade_result_path)
    with open(os.path.join(trade_result_path,f'{td.strftime("%Y%m%d")}_ResultTable.html'), 'w') as f:
        f.write(sum_table.get_html_string())

    text = f'\n【{td.strftime("%Y-%m-%d")}】策略損益\n'
    text += f'總損益(單部位) : {int(single_pnl)}\n'
    text += f'成交量(單部位) : {est_single_value}\n'
    text += f'總報酬(單部位) : {str(round((int(single_pnl) / est_single_value if est_single_value else 0) * 100, 2))}%\n\n'

    text += f'總損益(最大倉) : {int(max_pnl)}\n'
    text += f'成交量(最大倉) : {est_total_value}\n'
    text += f'總報酬(最大倉) : {str(round((int(max_pnl) / est_total_value if est_total_value else 0) * 100, 2))}%\n'
    
    Line.sendMessage(text)
    os._exit(0)