from shioaji import TickSTKv1, Exchange, BidAskSTKv1, TickFOPv1, BidAskFOPv1
from Messenger.LineMessenger import LineMessenger as Line

class sjFunc:
    
    def __init__(self, NotifyTickers):
        self.NotifyTickers = NotifyTickers
        
    def q20_callback(self, exchange:Exchange, tick:[TickSTKv1, TickFOPv1]):
        try:
            self.NotifyTickers[tick.code] = self.NotifyTickers.get(tick.code,
                                                    DataObject(tmp_contract, open_threshold=tmp_contract.reference, 
                                                    api=api, max_size = max_size_map[tick.code], PreData=open_thresholds[tick.code]))
            if type(tick) in [TickSTKv1, TickFOPv1]:
                self.NotifyTickers[tick.code].updateQ20Dict(dict(
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
        except Exception as e:
            print(e)
            
    def q80_callback(self, exchange:Exchange, tick:[BidAskSTKv1, BidAskFOPv1]):
        try:
            self.NotifyTickers[tick.code] = self.NotifyTickers.get(tick.code,
                                                    DataObject(tmp_contract, open_threshold=tmp_contract.reference, 
                                                    api=api, max_size = max_size_map[tick.code], PreData=open_thresholds[tick.code]))
            if type(tick) in [BidAskSTKv1, BidAskFOPv1]:
                self.NotifyTickers[tick.code].updateQ80Dict(dict(
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
        except Exception as e:
            print(e)
            
    def place_cb(self, stat, msg):
        try:
            if stat == sj.constant.OrderState.TFTOrder:
                if msg['order']['order_cond'] == 'Cash':
                    if msg['contract']['code'] in NotifyTickers.keys():
                        self.NotifyTickers[msg['contract']['code']].updateOrderDeal(stat, msg)
            else:
                if msg['order_cond'] == 'Cash':
                    if msg['code'] in NotifyTickers.keys():
                        self.NotifyTickers[msg['code']].updateOrderDeal(stat, msg)
        except:
            pass
        print(f"Order Status : {stat}, Order Data : {msg} \n")