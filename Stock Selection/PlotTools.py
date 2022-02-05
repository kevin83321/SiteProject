
from Calculator import Calculator
from utils import (
    fig_path, os, sendPhoto, GetException,
    plt, mpf, gridspec, mpl_ticker, 
    datetime, timedelta, date2num,
    mcolors, LineCollection, PolyCollection,
    TICKLEFT, TICKRIGHT, Line2D,
    Rectangle, Affine2D, xrange
)
from matplotlib.font_manager import fontManager, FontProperties
# for f in fontManager.ttflist:
#     print(f.name)
ChineseFont = FontProperties([f.name for f in fontManager.ttflist if 'JhengHei' in f.name or 'Heiti' in f.name or 'Arial ' in f.name][0])
# print([f.name for f in fontManager.ttflist if 'JhengHei' in f.name or 'Heiti' in f.name or 'Arial' in f.name])
# print(ChineseFont)

def plotVolume(ax, df):
    col = 'Adj_Volume' if 'Adj_Volume' in df.columns else 'Volume'
    df[col].plot(kind='bar', ax=ax)
    vol_ma_cols = [col for col in df.columns if 'Vol' in col and 'MA' in col]
    if vol_ma_cols:
        df[vol_ma_cols].plot(ax=ax)
    ax.legend(bbox_to_anchor=(1.1, 1.05))
    ax = splitTicksLabels(ax)
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=45 )
    ax.set_ylabel('Volume')
    return ax

def setuptitle(ax):
    setuplayout(ax)
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.set_ylabel('')
    ax.set_xlabel('')
    
def setuplayout(ax):
    ax.spines['top'].set_visible(False)  # .set_linewidth(2.0)
    ax.spines['bottom'].set_visible(False)  # .set_linewidth(2.0)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
def plotMACD(ax, df):
    if 'OSC' not in list(df.columns):
        df = Calculator.MACD(df)
    df[['MACD', 'DIF']].plot(ax=ax, legend=True)
    df['upOSC'] = df[df['OSC']>0]['OSC']
    df['downOSC'] = df[df['OSC']<=0]['OSC']
    df[['upOSC']].plot(ax=ax, kind='bar', color='r')
    df[['downOSC']].plot(ax=ax, kind='bar', color='g')
    ax.legend(bbox_to_anchor=(1.1, 1.05))
#     ax.xaxis.set_major_locator(mpl_ticker.MultipleLocator(5))
    ax = splitTicksLabels(ax)
    plt.setp( ax.xaxis.get_majorticklabels(), rotation=45 )
    ax.set_ylabel('Indicator')
    return ax

def splitTicksLabels(ax, per_num=15):
    for i, label in enumerate(ax.get_xticklabels()):
        if (i + 1) % per_num == 0:
            continue
        label.set_visible(False)
    return ax

def plotKBar(ax, df, BBAND=False):
    from copy import deepcopy
    df = deepcopy(df).reset_index()
    df.Date = df.Date.apply(transforDate)
    try:
        temp_df = df['Date,Open,High,Low,Close,Volume'.split(',')]
    except:
        temp_df = df['Date,Open,High,Low,Close'.split(',')]
    mpf.candlestick_ohlc(ax, [tuple(x.values()) for x in temp_df.T.to_dict().values()], 
                         colorup='r', colordown='g', width=0.8)
    plotMAs(ax, df.set_index('Date'))
    if BBAND:
        plotBBAND(ax, df.set_index('Date'))
    ax.legend(bbox_to_anchor=(1.1, 1.05))
    ax.set_ylabel('Price')
    
def plotMAs(ax, df):
    cols = [x for x in df.columns if 'MA' in x and 'EMA' not in x and 'MACD' not in x and 'Vol' not in x]
    if cols:
        df[cols].plot(ax=ax, legend = True)
        ax.legend(bbox_to_anchor=(1.1, 1.05))
    
def plotBBAND(ax, df, periods=20):
    cols = f'upband,dnband'.split(',')
    df[cols].plot(ax=ax, legend = True)
    ax.legend(bbox_to_anchor=(1.1, 1.05))
    
def transforDate(dt):
    return date2num(datetime.strptime(dt,'%Y-%m-%d'))

def plotTower(ax, df):
    setuptitle(ax)
    from copy import deepcopy
    df = deepcopy(df).reset_index()
    df.Date = df.Date.apply(transforDate)
    temp_df = df['Date,TowerO,TowerH,TowerL,TowerC'.split(',')].fillna(method='ffill')
    _candlestick(ax, [tuple(x.values()) for x in temp_df.T.to_dict().values()], 
                 width= 0.8, color_list = list(df.TColor))
    ax.legend(bbox_to_anchor=(1.1, 1.05))
    ax.set_ylabel('Tower Line')
    return ax

def _candlestick(ax, quotes, width=0.2, colorup='k', colordown='r',
                 alpha=1.0, ochl=False, color_list=None):
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown
    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of quote sequences
        data to plot.  time must be in float date format - see date2num
        (time, open, high, low, close, ...) vs
        (time, open, close, high, low, ...)
        set by `ochl`
    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level
    ochl: bool
        argument to select between ochl and ohlc ordering of quotes
    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added
    """

    OFFSET = width / 2.0

    lines = []
    patches = []
    for i, q in enumerate(quotes):
        if ochl:
            t, open, close, high, low = q[:5]
        else:
            t, open, high, low, close = q[:5]

        if close >= open:
            if color_list is not None:
                color = color_list[i]
            else:
                color = colorup
            lower = open
            height = close - open
        else:
            if color_list is not None:
                color = color_list[i]
            else:
                color = colordown
            lower = close
            height = open - close
        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - OFFSET, lower),
            width=width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)
    ax.autoscale_view()

    return lines, patches

def createPlot(td, df, ticker, MACD=False, TOWER=False, BBAND=False, extra_name=""):
    try:
        temp_df = df.tail(250)
        # plor chart
        fig = plt.figure(figsize=(16, 12))
        
        # set axis to be Clear
        plt.yticks([])
        plt.xticks([])
        # set title
        dayStr = (td+timedelta(1)).strftime("%Y-%m-%d")
        # text = f'Recommend {ticker} for follow up in next tradable day.'
        text = f'下一交易日追蹤標的 {ticker}, 其過去一年狀況'
        fig.suptitle(u'%s' %text, fontproperties=ChineseFont)
        
        num_subplot = 2
        if MACD:
            num_subplot += 1
        if TOWER:
            num_subplot += 1

        gs = gridspec.GridSpec(num_subplot, 3, wspace=0.25, hspace=0.25)

        # Plot Result
        ax1 = plt.subplot(gs[0, :])
        setuptitle(ax1)
        plotKBar(ax1, temp_df, BBAND=BBAND)
        
        # Plot Volume Bars
        ax2 = plt.subplot(gs[1, :])
        setuplayout(ax2)
        plotVolume(ax2, temp_df)

        # Plot MACD
        if num_subplot > 2:
            axs = []
            for i in range(2, num_subplot):
                axs.append(plt.subplot(gs[i, :]))
                setuplayout(axs[i-2])
                if MACD:
                    plotMACD(axs[i-2], temp_df)
                    MACD = False
                    continue
                if TOWER:
                    plotTower(axs[i-2], temp_df)
                    TOWER = False
                    continue
        
        # output Fig
        filename = f'{text} by {extra_name}.png' if len(extra_name) else f'{text}.png'
        full_path = os.path.join(fig_path, filename)
        
        plt.savefig(full_path)
        plt.show(block=False)
        plt.close()
        # sendPhoto(text, full_path)
    except:
        print(GetException())