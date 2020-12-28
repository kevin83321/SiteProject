__updated__ = '2020-12-29 00:44:33'
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
        pre_3y = td + timedelta(-30*6)
        df_twse = pd.DataFrame(TWSE_table.find({'IndexName':{'$eq':'發行量加權股價指數'},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))
        del df_twse['_id']
        df_twse = df_twse.set_index('Date')
        df_twse.index = pd.to_datetime(df_twse.index)
        
        # setup TAIFEX data
        schema = getSchema('TAIFEX')
        TAIFEX_table = schema['Interday.Future']
        TTM = getNearbyMaturity()
        df_tx = pd.DataFrame(TAIFEX_table.find({'Date':{'$gte':pre_3y.strftime('%Y/%m/%d'), '$lte':td.strftime('%Y/%m/%d')},
                                              'Contract':{'$eq':'TX'}, 
                                            #   'Maturity':{'$eq':TTM},
                                              #'TradingSession':{'$eq':'Regular'}
                                                }))
        df_tx = df_tx[(df_tx['Maturity'].apply(lambda x: str(x).strip()) == TTM) & (df_tx['TradingSession'] == 'Regular')]
        df_tx.index = range(len(df_tx))
        del df_tx['_id']
        df_tx = df_tx.set_index('Date')
        df_tx.index = pd.to_datetime(df_tx.index)
        
        # aggregate Data
        intersect_index = set(list(df_twse.index)).intersection(list(df_tx.index))
        df_twse = df_twse.reindex(index=intersect_index).sort_index()
        df_tx = df_tx.reindex(index=intersect_index).sort_index()
        signal = SPDStrategy(df_twse, df_tx)
        signal_map = {1:'多',-1:'空'}
        
        for col in 'Open,High,Low,Close'.split(','):
            df_twse[col] = df_twse[col].apply(changedType)
        last_Fut_preClose, last_Fut_Close = getTaiFut()
        last_mom = Calc.Momemtum(df_twse[:-1])
        mom = Calc.Momemtum(df_twse)
        momentums = [
            ('TWII '+last.strftime('%Y-%m-%d'), last_mom), 
            ('TWII '+td.strftime('%Y-%m-%d'), mom)
        ]
        preSpread = last_Fut_preClose - df_twse.Close.iloc[-2]
        Spread = last_Fut_Close - df_twse.Close.iloc[-1]
        diffSpread = Spread / preSpread -1
        delta_mom = (mom / last_mom) - 1
        expand_text = f'動量變化 : {round(delta_mom * 100, 2)} %\n'
        expand_text += f'期貨價格(昨收/今收) : {last_Fut_preClose} / {last_Fut_Close}\n'
        expand_text += f'前一日價差 : {round(preSpread, 2)}\n'
        expand_text += f'今日價差 : {round(Spread, 2)}\n'
        expand_text += f'價差變化 : {round(diffSpread * 100, 2)} %\n'
        expand_text += f'根據SPD計算，可以進場做"{signal_map[signal[-1]]}"\n'
        sendResultTable(td, ['TWII '+last.strftime('%Y-%m-%d'), 'TWII '+td.strftime('%Y-%m-%d')], 
                        momentums, '大', expand_text)
    except:
        print(GetException())
    
if __name__ == '__main__':
    main()
    
    