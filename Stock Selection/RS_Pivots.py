__updated__ = '2021-12-24 00:55:52'
from PlotTools import plt, plotKBar, transforDate, setuplayout, plotVolume, setuptitle, splitTicksLabels, equidate_ax#, date_tickers
# try:
from utils import (
    pd, np, timedelta, datetime, deepcopy, 
    GetData, mpl_dates, os, gridspec, ChineseFont,
    fig_path, GetException
)
import time
# except:
#     from TGBot.PlotUtils.utils import (
#         pd, np, timedelta, datetime, deepcopy, GetData, mpl_dates, os
#     )

parent = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(parent, 'OptionOI')
if not os.path.isdir(output_path):
    os.makedirs(output_path)

def getOptionOI(date:datetime=datetime.today()):
    df = pd.DataFrame()
    dtStr = date.strftime("%Y%m%d")
    isnet = False
    if date.isocalendar()[-1] <= 5:
        file_path = os.path.join(output_path, f'{dtStr}_OI.csv')
        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)
            for col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).strip())
        else:
            isnet = True
            url = f'https://www.taifex.com.tw/file/taifex/Dailydownload/LI/chinese/OPT/LI_{dtStr}.csv'
            try:
                df = pd.read_csv(url, encoding='cp950', skiprows=1)
            except:
                pass
            if not df.empty:
                if df.shape[1] == 1:
                    return pd.DataFrame(), isnet
                df.columns = 'Contract,C/P,TTM,Strike,OI,Volume,Liquitity'.split(',')
                for col in df.columns:
                    df[col] = df[col].apply(lambda x: str(x).strip())
                df.to_csv(file_path, index=False, encoding='utf-8')
    return df, isnet

def SeperateCP(date, df):
    df = df.copy(deep=True)
    df = df[df.Contract.apply(lambda x: x.strip()) == 'TXO']
    
    TTMs = sorted(df.TTM.astype(str).unique(), key=lambda x: str(x)[:6])
    closed_ttm = str(TTMs[0]).strip()
    ttm_year = int(closed_ttm[:4])
    ttm_month = int(closed_ttm[4:6])
    
    start_date = datetime(ttm_year, ttm_month, 1)
    next_month_date = start_date + timedelta(31)
    end_date = next_month_date.replace(day=1) + timedelta(-1)
    ttm_dates = pd.date_range(start_date, end_date, freq="W-WED")
    if "W" in closed_ttm:
        ttm_date = ttm_dates[1]
    else:
        ttm_date = ttm_dates[2]
    if date.date() == ttm_dates[0].date():#[x.date() for x in ]:
        closed_ttm = TTMs[1]
    if "W" in closed_ttm:
        closed_ttm = TTMs[1]
    tmp_df = df[df.TTM.astype(str) == closed_ttm]
    call_df = tmp_df[tmp_df['C/P']=='買權']
    call_df.OI = call_df.OI.apply(lambda x: float(x))
    call_df = call_df.sort_values("OI", ascending=False).head(10)
    put_df = tmp_df[tmp_df['C/P']=='賣權']
    put_df.OI = put_df.OI.apply(lambda x: float(x))
    put_df = put_df.sort_values("OI", ascending=False).head(10)
    return call_df, put_df, closed_ttm, ttm_date

def AggregateOI(date, df):
    call_df, put_df, closed_ttm, ttm_date = SeperateCP(date, df)
    output = {
        'Date':date,
        "TTM":closed_ttm,
        'MaxOIStrikeCall':call_df.loc[call_df.index[0], 'Strike'],
        'MaxOICall':float(call_df.loc[call_df.index[0], 'OI']),
        'TotalOICall':call_df.OI.apply(lambda x: float(x)).sum(),
        'VWStrikeCall':(call_df.OI.apply(lambda x: float(x)) * call_df.Strike.apply(lambda x: float(x))).sum() / call_df.OI.apply(lambda x: float(x)).sum(),
        'MaxOIStrikePut':put_df.loc[put_df.index[0], 'Strike'],
        'MaxOIPut':float(put_df.loc[put_df.index[0], 'OI']),
        'TotalOIPut':put_df.OI.apply(lambda x: float(x)).sum(),
        'VWStrikePut':(put_df.OI.apply(lambda x: float(x)) * put_df.Strike.apply(lambda x: float(x))).sum() / put_df.OI.apply(lambda x: float(x)).sum(),
        "IsTTM":int(date.date() == ttm_date.date()),
    }
    return output

def ReadOptOIAll(dates):
    Option_oi = {}
    aggregate_data = []
    for date in dates:
        print(f"========= Read {date.strftime('%Y-%m-%d')} =========")
        Option_oi[date], isnet = getOptionOI(date)
        if isnet:
            time.sleep(3)

    for date, df in Option_oi.items():
        if df.empty:
            continue
        aggregate_data.append(AggregateOI(date, df))

    return pd.DataFrame(aggregate_data)#.set_index('Date')

#======================================
# method 1: fractal candlestick pattern
#======================================

# determine bullish fractal 
def is_support(df,i):  
    cond1 = df['Low'][i] < df['Low'][i-1]   
    cond2 = df['Low'][i] < df['Low'][i+1]   
    cond3 = df['Low'][i+1] < df['Low'][i+2]   
    cond4 = df['Low'][i-1] < df['Low'][i-2]  
    return (cond1 and cond2 and cond3 and cond4) 

# determine bearish fractal
def is_resistance(df,i):  
    cond1 = df['High'][i] > df['High'][i-1]   
    cond2 = df['High'][i] > df['High'][i+1]   
    cond3 = df['High'][i+1] > df['High'][i+2]   
    cond4 = df['High'][i-1] > df['High'][i-2]  
    return (cond1 and cond2 and cond3 and cond4)

# to make sure the new level area does not exist already
def is_far_from_level(value, levels, df):    
    ave =  np.mean(df['High'] - df['Low'])    
    return np.sum([abs(value-level)<ave for _,level in levels])==0

def calculateLevels(df):
    # a list to store resistance and support levels
    levels = []
    for i in range(2, df.shape[0] - 2):  
        if is_support(df, i):    
            low = df['Low'][i]
            if is_far_from_level(low, levels, df):
                levels.append((i, low))
        elif is_resistance(df, i):
            high = df['High'][i]
            if is_far_from_level(high, levels, df):
                levels.append((i, high))
    return levels

def calculatePivots(df):
    pivots = []
    max_list = []
    min_list = []
    for i in range(5, len(df)-5):
        # taking a window of 9 candles
        high_range = df['High'][i-5:i+4]
        current_max = high_range.max()

        # if we find a new maximum value, empty the max_list 
        if current_max not in max_list:
            max_list = []
        max_list.append(current_max)

        # if the maximum value remains the same after shifting 5 times
        if len(max_list)==5 and is_far_from_level(current_max,pivots,df):
            pivots.append((high_range.idxmax(), current_max))

        low_range = df['Low'][i-5:i+5]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list)==5 and is_far_from_level(current_min,pivots,df):
            pivots.append((low_range.idxmin(), current_min))
    return pivots

def plot_all(ax, levels, df, ticker, expand_text=""):
    try:
        # global date_tickers
        df = deepcopy(df)
        # fig, ax = plt.subplots(figsize=(16, 9))
        plotKBar(ax, df)#.set_index("Date"))
        # date_tickers = df.Date.values
        df['DateStr'] = df.Date
        df.Date = df.Date.apply(transforDate)
        for i in range(len(levels)):
            next_level = None
            level = levels[i]
            try:
                next_level = levels[i+1]
            except:
                pass
            xmax = df['Date'].max()
            if next_level:
                if str(next_level[0]).isnumeric():
                    xmax = df['Date'][next_level[0]]
                else:
                    xmax = df[df.DateStr == next_level[0]].Date
            if str(level[0]).isnumeric():
                xmin = df['Date'][level[0]]
            else:
                xmin = df[df.DateStr == level[0]].Date
            plt.hlines(level[1], xmin = xmin, xmax = xmax, colors='blue', linestyle='--')
    except:
        pass

def plot_oi_RS(ax, oi_df):
    try:
        df = oi_df.copy(deep=True)
        df['DateStr'] = df.Date
        df.Date = df.Date.apply(transforDate)
        for col in 'VWStrikePut,VWStrikeCall'.split(','): # ,MaxOIStrikeCall,MaxOIStrikePut
            ax.plot(df.Date, df[col].astype(float), label=col)

        expire_dates = []
        for i, row in enumerate(df.itertuples()):
            if not i: continue
            if not np.isnan(float(row.TTM)):
                if row.TTM != df.loc[df.index[i-1], "TTM"]:
                    expire_dates.append(row.Date)
        for x in expire_dates:
            ax.vlines(x,
                    df['VWStrikePut,MaxOIStrikePut'.split(',')].astype(float).min(axis=1).min(),
                    df['VWStrikeCall,MaxOIStrikeCall'.split(',')].astype(float).max(axis=1).max(),
                    color='yellow',
        #               label='Expire Date'
                    )

        ax.legend(bbox_to_anchor=(1.1, 1.05))
    except Exception as e:
        print(e)
    
def mainPlot(ticker, td=datetime.today(), extra_name="", df = None):
    try:
        # print('in mainplot', ChineseFont)
        if df is None:
            df = GetData(ticker, td)
        if df.empty:
            df = GetData(ticker, td)
        df = df.reset_index()
        oi_df = ReadOptOIAll(pd.to_datetime(df.Date))
        df.Date = df.Date.apply(lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime) else x) # pd.to_datetime(df.Date) #
        oi_df.Date = oi_df.Date.apply(lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime) else x) # pd.to_datetime(df.Date) #
        levels = calculatePivots(df)
        # temp_df = df.tail(250)
        # plor chart
        fig = plt.figure(figsize=(16, 12))
        
        # set axis to be Clear
        plt.yticks([])
        # plt.xticks([])
        # set title
        dayStr = (td+timedelta(1)).strftime("%Y-%m-%d")
        # text = f'Recommend {ticker} for follow up in next tradable day.'
        text = f'{ticker} 其過去一年的支撐壓力'
        fig.suptitle(u'%s' %text, fontproperties=ChineseFont)
        
        gs = gridspec.GridSpec(2, 3, wspace=0.25, hspace=0.25)

        
        # print(levels)
        # Plot Volume Bars
        if "Volume" in df.columns:
            # Plot Result
            ax1 = plt.subplot(gs[0, :])
            setuptitle(ax1)
            plot_all(ax1, levels, df.reset_index(), ticker)
            ax2 = plt.subplot(gs[1, :])
            setuplayout(ax2)
            plotVolume(ax2, df)
            plt.setp( ax2.xaxis.get_majorticklabels(), rotation=45 )
        else:
            # Plot Result
            ax1 = plt.subplot(gs[:, :])
            setuptitle(ax1)
            plot_all(ax1, levels, df.reset_index(), ticker)
            plot_oi_RS(ax1, oi_df.reset_index())
            equidate_ax(fig, ax1, df.Date, fmt="%Y-%m-%d", label="Date")
            setuplayout(ax1)
            splitTicksLabels(ax1)
            plt.setp( ax1.xaxis.get_majorticklabels(), rotation=45 )

        
        date_format = mpl_dates.DateFormatter('%d %b %Y')
        try:
            ax2.xaxis.set_major_formatter(date_format) 
        except:
            pass
        ax1.xaxis.set_major_formatter(date_format) 
        
        # output Fig
        filename = f'{text} by {extra_name}.png' if len(extra_name) else f'{text}.png'
        full_path = os.path.join(fig_path, filename)
        
        plt.savefig(full_path)
        plt.show(block=False)
        plt.close()
        return full_path
    except:
        print(GetException())



if __name__ == "__main__":
    mainPlot(ticker="2330")