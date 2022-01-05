__updated__ = '2021-02-01 22:24:07'
from Calculator import Calculator as Calc
from PlotTools import createPlot
from utils import (
    pd, np, getSchema, getDateBeforeTrade, 
    saveRecommand, timedelta, GetException,
    sendResultTable, changedType, createRecommandTable, 
    datetime, os
)
from crawler import getTaiFut
import pandas_datareader.data as web
import calendar


def getNearbyMonth():
    td = datetime.today()
    month = td.month
    if isTimetoMaturity(td): 
        month += 1
    if month > 12:
        month = 1
    return month

def isTimetoMaturity(td):
    thirdWendesday = getThirdWendesday(td)
    if td.strftime('%Y%m%d') >= thirdWendesday.strftime('%Y%m%d'): return True
    return False

def getThirdWendesday(td):
    first_day_of_month = datetime(td.year, td.month, 1)
    firstWendesday = first_day_of_month + timedelta(days=((2-calendar.monthrange(td.year, td.month)[0])+7)%7)
    return firstWendesday + timedelta(days=14)

def getNearbyMaturity():
    month = getNearbyMonth()
    td = datetime.today()
    if td.replace(month=month) < td:
        return td.replace(year=td.year+1, month=month).strftime('%Y%m')
    return td.replace(month=month).strftime('%Y%m')

class ATR:
    
    def __init__(self, n=14):
        self.n = n
        self.tr = []
        
    def update(self, high, low, close):
        self.tr.append(max((high - low), abs(high - close), abs(low - close)))
        if len(self.tr) >= self.n:
            self.atr_ = np.mean(self.tr)
            self.tr.pop(0)
    
    @property
    def atr(self):
        return self.atr_
    
    
def SPDStrategy(s_data, f_data, k1=0.3125, k2=0.0025, k3=15):
    """
    Spread Trading, Freq = Day
    """
    signal = flag = 0
    result = []
    pre_date = None
    atr = ATR(k3)
    signals = []
    for i, (s_row, f_row) in enumerate(list(zip(s_data.itertuples(), f_data.itertuples()))):
        atr.update(f_row.High, f_row.Low, f_row.Close)
        if i < k3: 
            signals.append(0)
            continue
        if pre_date is None: pre_date = f_row.Index
        spd = f_row.Close - s_row.Close
        atr_ = atr.atr
        up = f_row.Open + k1 * atr_ # long
        dn = f_row.Open - k2 * atr_ # short
        tempProfit = 0
        exitDate = None
        
        # calculate signal without position
        if signal == 0:
            signal = -np.sign(spd) if spd != 0 else 0
        # entry market
        elif signal !=0:
            if signal > 0:
                if f_row.Open >= up:
                    signals.append(signal)
                elif f_row.Close >= up:
                    signals.append(signal)
            elif signal < 0:
                if f_row.Open <= dn:
                    signals.append(signal)
                elif f_row.Close <= dn:
                    signals.append(signal)
            signal = 0
            if len(signals) == i:
                signals.append(signal)
    return signals

def main():
    try:
        # setup date
        td, last = getDateBeforeTrade()
        
        # setup TWSE data
        schema = getSchema('TWSE')
        TWSE_table = schema['HistoricalPrice.Index.Interday']
        pre_3y = td + timedelta(-365*3)
        df_twse = pd.DataFrame(TWSE_table.find({'IndexName':{'$eq':'發行量加權股價指數'},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
        del df_twse['_id']
        df_twse = df_twse.set_index('Date')
        df_twse.index = pd.to_datetime(df_twse.index)
        
        # print(df_twse)
        df_twse.Close = df_twse.Close.replace('--', float('nan')).astype(float)
        df_twse.High = df_twse.High.replace('--', float('nan')).astype(float)
        df_twse.Low = df_twse.Low.replace('--', float('nan')).astype(float)
        df_twse.Open = df_twse.Open.replace('--', float('nan')).astype(float)
        max_oc = df_twse[['Close', 'Open']].max(axis=1)
        df_twse = Calc.MA(df_twse, [5,10, 20])
        df_twse = Calc.EMA(df_twse, [23, 67])
        df_twse = Calc.BBAND(df_twse, 20, 2)
        df_twse['slope_20'] = df_twse['MA20'].pct_change()
        df_twse['slope_5'] = df_twse['MA5'].pct_change()
        
        ## Short Sell Signal
        # print(max_oc.iloc[-3], max_oc.iloc[-1],  max_oc.iloc[-2])
        SScondi1 = max(df_twse.Close.iloc[-3], df_twse.Close.iloc[-1]) < df_twse.Close.iloc[-2] # temp_df.slope5.pct_change().iloc[-1] < 0#
        SScondi2 = (max_oc.iloc[-2] / max_oc.iloc[-10] - 1) >= .01
        # SScondi3 = (df_twse.upband.iloc[-2] / df_twse.dnband.iloc[-2] - 1) >= .05
        SScondi4 = df_twse.Close.iloc[-1] < df_twse.MA10.iloc[-1]
        # print(SScondi1,(max_oc.iloc[-2] / max_oc.iloc[-10] - 1))
        mom = Calc.Momemtum(df_twse)
        final_select = ["TWSE"]
        momentums = [("TWSE", mom)]
        expand_text = ""
        if all([SScondi1, SScondi2, SScondi4]): #, SScondi3
            expand_text += "短空訊號 : 頭部位置(短波段(10日)漲幅 >= 1%)，近一日收黑K\n"

        SSCondi1 = df_twse.Close.iloc[-2] >= df_twse.EMA67.iloc[-2] and df_twse.Close.iloc[-1] <= df_twse.EMA67.iloc[-1]
        SSCondi2 = (df_twse.Close.iloc[-1] / df_twse.Close.iloc[-5]) - 1 <= -0.05
        if all([SSCondi1, SSCondi2]):
            expand_text += "短空進長空訊號 : 腰部位置(波段(5日)跌幅 >= 5%)，近一日收黑K\n"

        # Long Signal
        Bcondi_1 = df_twse['slope_20'][-2] < 0 and df_twse['slope_5'][-2] < 0
        Bcondi_2 = df_twse['Low'][-2] <= df_twse['dnband'][-2] <= df_twse['High'][-2] or (df_twse['Low'][-2] > df_twse['dnband'][-2] and df_twse['Low'][-2] / df_twse['dnband'][-2] - 1 <= 0.05)
        Bcondi_3 = df_twse['Low'][-1] >= df_twse['dnband'][-1]
        Bcondi_4 = df_twse['Close'].pct_change()[-1] > 0
        if all([Bcondi_1, Bcondi_2, Bcondi_3, Bcondi_4]):
            expand_text += "反彈訊號 : 布林底部反轉，可小試多單\n"

        BBCondi1 = df_twse.Close.iloc[-2] <= df_twse.EMA67.iloc[-2] and df_twse.Close.iloc[-1] >= df_twse.EMA67.iloc[-1]
        BBCondi2 = (df_twse.Close.iloc[-1] / df_twse.Close.iloc[-5]) - 1 >= 0.05
        if all([BBCondi1, BBCondi2]):
            expand_text += "短多進長多訊號 : 腰部位置(波段(5日)漲幅 >= 5%)，近一日收紅K\n"

        if len(expand_text):
            expand_text += "進場，一律注意停損，自設可接受範圍"

        sendResultTable(td, final_select, momentums, '大', expand_text=expand_text)
    except:
        print(GetException())
    
if __name__ == '__main__':
    main()