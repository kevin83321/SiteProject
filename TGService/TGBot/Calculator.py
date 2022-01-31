from .utils import GetException, np

class Calculator:
    
    @staticmethod
    def MACD(df, inp_col = 'DI'):
        try:
            if inp_col == 'DI':
                df = Calculator.DI(df)
            df = Calculator.EMA(df, [12, 26], inp_col)
            df['DIF'] = df.EMA12 - df.EMA26
            df['MACD'] = df.DIF.ewm(span=9).mean()
            df['OSC'] = (df.DIF - df.MACD)
        except:
            print(GetException())
        else:
            return df
        
    @staticmethod
    def DI(df):
        try:
            df['DI'] = (df.High.astype(float) + df.Low.astype(float) + 2 * df.Close.astype(float)) / 4
        except:
            print(GetException())
        else:
            return df
    
    @staticmethod
    def MA(df, mas, inp_col:str=None):
        try:
            if inp_col is None:
                inp_col = 'Close'
            if isinstance(mas, list):
                for ma in mas:
                    df[f'MA{ma}'] = df[inp_col].rolling(ma).mean()
            if isinstance(mas, (int, float)):
                df[f'MA{ma}'] = df[inp_col].rolling(mas).mean()
        except:
            print(GetException())
        else:
            return df
        
    @staticmethod
    def EMA(df, emas, inp_col:str=None):
        try:
            if inp_col is None:
                inp_col = 'Close'
            if isinstance(emas, (list, tuple)):
                for ema in emas:
                    df[f'EMA{ema}'] = df[inp_col].ewm(span=ema).mean()
            if isinstance(emas, (int, float)):
                df[f'EMA{ema}'] = df[inp_col].ewm(span=emas).mean()
        except:
            print(GetException())
        else:
            return df
        
    @staticmethod
    def BBAND(df, periods, k):
        try:
            if f'MA{periods}' not in df.columns:
                df = Calculator.MA(df, [periods])
            df['std'] = df.Close.rolling(periods).std()
            df['upband'] = df[f'MA{periods}'] + k * df['std']
            df['dnband'] = df[f'MA{periods}'] - k * df['std']
            df['bandwidth'] = df['upband'] / df['dnband'] - 1
        except:
            print(GetException())
        else:
            return df        
        
    @staticmethod
    def calculateTOWER(df, lookback=3, version = 'Def'):
        df['TowerH'] = np.nan
        df['TowerL'] = np.nan
        df['TowerO'] = df.Close.shift(1)
        df['TowerC'] = df.Close
        df['Tower'] = np.nan
        df['TColor'] = np.nan
        highs, lows = [], []
        pre_row = None
        for (i, row) in enumerate(list(df.itertuples())):
            highs.append(row.High); lows.append(row.Low)
            if pre_row is None:
                pre_row = row
                if version == 'XQ':
                    highs[-1] = row.Close
                    lows[-1] = row.Close
                continue
            if row.TowerC > row.TowerO:
                df.loc[row.Index,'TowerH'] = row.TowerC
                df.loc[row.Index,'TowerL'] = row.TowerO
                df.loc[row.Index,'Tower'] = 'U'
                if version == 'XQ':
                    highs[-1] = row.TowerC
                    lows[-1] = row.TowerO
            elif row.TowerC < row.TowerO:
                df.loc[row.Index,'TowerH'] = row.TowerO
                df.loc[row.Index,'TowerL'] = row.TowerC
                df.loc[row.Index,'Tower'] = 'D'
                if version == 'XQ':
                    highs[-1] = row.TowerO
                    lows[-1] = row.TowerC
            else:
                df.loc[row.Index,'TowerH'] = row.TowerC+0.0001
                df.loc[row.Index,'TowerL'] = row.TowerC-0.0001
                df.loc[row.Index,'Tower'] = 'K'
                if version == 'XQ':
                    highs[-1] = row.Close
                    lows[-1] = row.Close
            
            if i <= lookback-1:
                if df.loc[row.Index, 'Tower'] == 'U':
                    df.loc[row.Index, 'TColor'] = 'r'
                elif df.loc[row.Index, 'Tower'] == 'D':
                    df.loc[row.Index, 'TColor'] = 'g'
                else: # Tower == K
                    df.loc[row.Index, 'TColor'] = df.loc[pre_row.Index, 'TColor']
                pre_row = row
                continue
            else:
                min_Low = min(lows[:3])
                max_High = max(highs[:3])
                
                if df.loc[row.Index, 'Tower'] == 'D':
                    df.loc[row.Index, 'TColor'] = 'g'
                    if df.loc[pre_row.Index, 'TColor'] == 'r':
                        df.loc[row.Index, 'TColor'] = 'r'
    #                     if row.TowerC <= min_Low: # 收盤小於前n天最高
                        if row.Close <= min_Low: # 收盤小於前n天最高
                            df.loc[row.Index, 'TColor'] = 'g'
                elif df.loc[row.Index, 'Tower'] == 'U':
                    df.loc[row.Index, 'TColor'] = 'r'
                    if df.loc[pre_row.Index, 'TColor'] == 'g':
                        df.loc[row.Index, 'TColor'] = 'g'
    #                     if row.TowerC >= max_High: # 收盤大於前n天最高
                        if row.Close >= max_High: # 收盤大於前n天最高
                            df.loc[row.Index, 'TColor'] = 'r'
                else: # Tower == 'K'
                    df.loc[row.Index, 'TColor'] = df.loc[pre_row.Index, 'TColor']
                lows.pop(0)
                highs.pop(0)
            pre_row = row
            df.TColor = df.TColor.fillna(method='ffill')       
        return df
    
    @staticmethod
    def Momemtum(df, months:list=[1,3,6], weights:list=[.33, .34, .33]) -> float:
        try:
            if isinstance(months, list):
                if isinstance(weights, list):
                    Ret = df.Close.fillna(method='ffill').dropna().pct_change()
                    mom = sum([((Ret[-m * 21:] + 1).product() - 1) * w for m, w in zip(months, weights)])
        except:
            print(GetException())
            # print(df)
        else:
            return mom

    @staticmethod
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

    @staticmethod
    def CalculateUpDnLimit(price, up_ratio=0.1, down_ratio=0.1):
        tmp_up = tmp_dn = price
        while 1:
            tmp_tick_up = Calculator.get_minimum_tick(tmp_up)
            tmp_up = round(tmp_up+tmp_tick_up,2)
            if tmp_up / price > 1 + up_ratio:
                up_limit = tmp_up - tmp_tick_up
                break

        while 1:
            tmp_tick_dn = Calculator.get_minimum_tick(tmp_dn)
            # tmp_dn -= tmp_tick_dn
            tmp_dn = round(tmp_dn - tmp_tick_dn,2)
            if tmp_dn / price < 1 - down_ratio:
                dn_limit = tmp_dn + tmp_tick_dn
                break
        return round(up_limit, 2), round(dn_limit, 2)