from platform import system
if system() == 'Darwin':
    import matplotlib
    matplotlib.use("MacOSX")
import matplotlib.pyplot as plt
import mpl_finance as mpf
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mpl_ticker

from prettytable import PrettyTable

from matplotlib import colors as mcolors
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import TICKLEFT, TICKRIGHT, Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D
import matplotlib.dates as mpl_dates
from matplotlib.pylab import date2num # 导入日期到数值一一对应的转换工具
from matplotlib.font_manager import fontManager, FontProperties
ChineseFont = FontProperties([f.name for f in fontManager.ttflist if 'JhengHei' in f.name or 'Heiti' in f.name or 'Arial ' in f.name][0])
print(ChineseFont)

try:
    from TGBot.Log.TransforException import GetException
    from TGBot.utils import getSchema, deepcopy, pd, np, datetime, timedelta, os
except:
    from ..Log.TransforException import GetException
    from ..utils import getSchema, deepcopy, pd, np, datetime, timedelta, os

parent = os.path.dirname(os.path.abspath(__file__))
fig_path = os.path.join(parent, "FigOutput")
if not os.path.isdir(fig_path):
    os.makedirs(fig_path)


def GetData(ticker, td = datetime.today(), years=1):
    # setup data
    schema = getSchema('TWSE')
    table = schema['historicalPrice']
    pre_3y = td + timedelta(-365*years)
    temp_df = pd.DataFrame(list(table.find({'Ticker':{'$eq':ticker},'Date':{'$gte':pre_3y.strftime('%Y-%m-%d'), '$lte':td.strftime('%Y-%m-%d')}}))).set_index('Date')
    for col in "Open,High,Low,Close,Volume".split(','):
        temp_df[col] = temp_df[col].apply(changedType)
    return temp_df

def changedType(x):
    try:
        if '--' in x:
            return float('nan')
        if isinstance(x, str):
            return float(x.replace(',',''))
        return x
    except:
        return x