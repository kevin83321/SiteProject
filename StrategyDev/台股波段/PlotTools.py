
from Calculator import Calculator
from utils import (
    fig_path, os, sendPhoto, GetException,
    plt, mpf, gridspec, mpl_ticker, 
    datetime, timedelta, date2num,
    mcolors, LineCollection, PolyCollection,
    TICKLEFT, TICKRIGHT, Line2D,
    Rectangle, Affine2D, xrange, fig_path
)
from pprint import pprint
from matplotlib.font_manager import fontManager, FontProperties
# for f in fontManager.ttflist:
#     print(f.name)
ChineseFont = FontProperties([f.name for f in fontManager.ttflist if 'JhengHei' in f.name or 'Heiti' in f.name][0]) #  or 'Arial' in f.name


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
    temp_df = df['Date,Open,High,Low,Close,Volume'.split(',')]
    mpf.candlestick_ohlc(ax, [tuple(x.values()) for x in temp_df.T.to_dict().values()], 
                         colorup='r', colordown='g', width=0.8)
    plotMAs(ax, df.set_index('Date'))
    if BBAND:
        plotBBAND(ax, df.set_index('Date'))
    ax.legend(bbox_to_anchor=(1.1, 1.05))
    ax.set_ylabel('Price')
    
def plotMAs(ax, df):
    cols = [x for x in df.columns if 'MA' in x and 'EMA' not in x and 'MACD' not in x and 'Vol' not in x]
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

def CreateRecommendFig(td, tickers, bt_Prob=[], holding_p=[], highProb=[],InvestorOB=[], InvestorOBF=[], 
                        algo_num=1, description='', entry_method='', take_profit_rate=10, 
                        stop_loss_rate=10, algo_name=''):
    """
    產生選股建議全表
    """
    tmp_h_prob = dict(highProb)
    tmp_bt_prob = dict(bt_Prob)
    tmp_holing_p = dict(holding_p)
    tmp_OB = dict(InvestorOB)
    tmp_OBF = dict(InvestorOBF)
    tmp_ob = [tmp_OB.get(ticker, "N") for ticker in tickers] # high win probability
    tmp_obf = [tmp_OBF.get(ticker, "N") for ticker in tickers] # high win probability
    h_prob = [tmp_h_prob.get(ticker, "N") for ticker in tickers] # high win probability
    bt_prob = [round(tmp_bt_prob.get(ticker, 0), 2) for ticker in tickers]  # backtest win probability
    h_p = [round(tmp_holing_p.get(ticker, 0),2) for ticker in tickers] # holding period
    return PlotResult(td, tickers, bt_prob, h_p, h_prob, tmp_ob, tmp_obf, algo_num, description, entry_method, take_profit_rate, stop_loss_rate, algo_name)


def PlotResult(dt:datetime.today(), tickers=[], bt_Prob=[], holding_p=[], highProb=[], 
                InvestorOB=[], InvestorOBF=[], algo_num=1, 
                description='', entry_method='', take_profit_rate=10, stop_loss_rate=10,
                algo_name=''):
    try:
        if not tickers: return ''
        # Create Figure
        fig = plt.figure(figsize=(10, 14), dpi=600)
        # fig.set_size_inches(1024,864)
        # set axis to be Clear
        plt.yticks([])
        plt.xticks([])
        # set title
        dtStr = dt.strftime("%Y-%m-%d")
        fig.suptitle(f'無腦秘書{algo_num}號 {dtStr} 選股建議', fontproperties=ChineseFont)

        gs = gridspec.GridSpec(3, 3, wspace=0.25, hspace=0.25)
        # Plot Recommand Table
        ax1 = plt.subplot(gs[:2, :])
#         ax1.title.set_text(f'{dtStr} 選股建議')
#         ax1.title.set_font_properties(ChineseFont)
        setuptitle(ax1)
        PlotTable_v2(ax1, tickers, bt_Prob, holding_p, highProb, InvestorOB, InvestorOBF)

        # Plot Description
        ax3 = plt.subplot(gs[2:, :])
        ax3.title.set_text('選股使用說明')
        ax3.title.set_font_properties(ChineseFont)
        PlotDiscriptionTXT(ax3, description, entry_method, take_profit_rate, stop_loss_rate)
    except:
        print(GetException())
    else:
        # dt = datetime.today()
        # fig_path = os.path.join(output_path, str(dt.year).zfill(
        #     4), str(dt.month).zfill(2), str(dt.day).zfill(2))
        if not os.path.isdir(fig_path):
            os.makedirs(fig_path)
        plt.tight_layout()
        
        plt.savefig(os.path.join(
            fig_path, f'{algo_name} Stock Suggestion.jpg'))
        # plt.show()
        plt.show(block=False)
        plt.close()
        return os.path.join(fig_path, f'{algo_name} Stock Suggestion.jpg')

def PlotTable_v2(ax, tickers, bt_Prob=[], holding_p=[], highProb=[],InvestorOB=[], InvestorOBF=[], split_num=25):
    try:
        data = []
        base_cols = ['代號','回測勝率','平均持倉時間(日)','高勝率低週期推薦','投信買超','外資買超']
        tmp_d = zip(tickers, bt_Prob, holding_p, highProb, InvestorOB, InvestorOBF)
        if len(tickers)>=split_num*2:
            if len([x for x in highProb if x == 'Y']):
                tmp_d = [x for x in tmp_d if x[-1] == 'Y']
            else:
                tmp_d = [x for x in tmp_d if float(x[2]) <= 40]
        tmp_d = sorted(tmp_d, key=lambda x : x[-2])
        if not (len(list(tmp_d))) : return ''
        seperate_num = int(len(list(tmp_d)) / split_num)
        # columns = base_cols * (seperate_num + 1)
        # print(seperate_num, len(list(tmp_d)))
        for i, (ticker, bt_p, hold_p, high_p, ob_, ob_f) in enumerate(tmp_d):
            try:
                if i >= split_num:
                    data[i-split_num].extend([ticker, bt_p, hold_p, high_p, ob_, ob_f])
                else:
                    data.append([ticker, bt_p, hold_p, high_p, ob_, ob_f])
            except:
                pass
        # pprint(data)
        max_width = max([len(x) for x in data])
        # print(max_width)
        columns = base_cols * int(max_width / len(base_cols))
        for i in range(len(data)):
            # print(data[i], len(data[i]), len(columns))
            if len(data[i]) != len(columns):
                data[i].extend(['',]*(len(columns)-len(base_cols)))
            # print(data[i])
        # pprint(data)
        # print(len(data[0]))
        # print(len(data[-1]))
        # print(len(columns))
#         columns = ['回測勝率','平均持倉時間(日)','高勝率低持倉推薦']
        
        # rows = tickers
        the_table = ax.table(cellText=data,
                                rowLabels=list(range(1, min(split_num, len(tickers)) + 1)),
                                colLabels=columns,
                                loc='center',
                                fontsize=16,
                                cellLoc='center',
                                rowLoc='center',
                                colLoc='center',
                                colWidths=[.1, ]*len(columns),
                                )
        
        table_props = the_table.properties()
        table_cells = table_props['children']
        for i, cell in enumerate(table_cells):
#             if not i:
#                 help(cell.set_text_props)
            cell.set_height(0.03)
            cell.set_text_props(fontproperties=ChineseFont, fontsize=16)

        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.set_ylabel('')
        ax.set_xlabel('')
    except:
        print(GetException())

def setuptitle(ax):
    ax.spines['top'].set_visible(False)  # .set_linewidth(2.0)
    ax.spines['bottom'].set_visible(False)  # .set_linewidth(2.0)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.set_ylabel('')
    ax.set_xlabel('')


def PlotDiscriptionTXT(ax, description, entry_method, take_profit_rate=10, stop_loss_rate=10):
    try:
        ax.text(4.6, 18, f'選股說明 : ',
                fontsize=11, horizontalalignment='right', fontweight='bold', fontproperties=ChineseFont)
        ax.text(4.8, 18, f'{description}',
                fontsize=11, horizontalalignment='left', fontweight='bold', fontproperties=ChineseFont)
        
        ax.text(4.6, 16, f'進場方式 : ', fontsize=11,
                horizontalalignment='right', fontproperties=ChineseFont)
        ax.text(4.8, 16, f'{entry_method}', fontsize=11,
                horizontalalignment='left', fontproperties=ChineseFont)
        
        # Describe Max Return Portfolio
        ax.text(4.6, 14, f'出場方式-停利 : ',
                fontsize=11, horizontalalignment='right', fontweight='bold', fontproperties=ChineseFont)
        ax.text(4.8, 14, f'{take_profit_rate}%',
                fontsize=11, horizontalalignment='left', fontweight='bold', fontproperties=ChineseFont)
        
        ax.text(4.6, 12, f'出場方式-停損 : ',
                fontsize=11, horizontalalignment='right', fontproperties=ChineseFont)
        ax.text(4.8, 12, f'{stop_loss_rate}%',
                fontsize=11, horizontalalignment='left', fontproperties=ChineseFont)
        
        # Describe Min Std Portfolio
        ax.text(4.6, 10, '備註 : ',
                fontsize=11, horizontalalignment='right', fontweight='bold', fontproperties=ChineseFont)
        ax.text(4.8, 10, '此選股尚未考慮除權息，若遇除權息打到停損，請等填息再出場(股價回到除權息前的價格)',
                fontsize=11, horizontalalignment='left', fontweight='bold', fontproperties=ChineseFont)
        ax.text(4.8, 8, '推薦欄為Y者，屬於低週期高勝率，且10年內有20次以上的交易次數(年均2次)，優先選擇',
                fontsize=11, horizontalalignment='left', fontweight='bold', fontproperties=ChineseFont)
        ax.text(4.8, 6, '推薦欄為N者，但想入場，建議同樣選擇低週期高勝率之標的',
                fontsize=11, horizontalalignment='left', fontweight='bold', fontproperties=ChineseFont)
        ax.text(4.8, 4, '所選標的皆已排除10年內交易次數少於10次之標的(沒人玩)',
                fontsize=11, horizontalalignment='left', fontweight='bold', fontproperties=ChineseFont)

        ax.spines['top'].set_linewidth(2.0)
        ax.spines['bottom'].set_linewidth(2.0)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.axis([0, 20, 0, 20])
    except:
        print(GetException())