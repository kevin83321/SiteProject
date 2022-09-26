import matplotlib as mpl
import matplotlib.pyplot as plt
from Utils import pd, np, output_path, os

from matplotlib.font_manager import fontManager, FontProperties
ChineseFont = FontProperties([f.name for f in fontManager.ttflist if 'JhengHei' in f.name or 'Heiti' in f.name][0]) #  or 'Arial' in f.name

def mergecells(table, cells):
    '''
    Merge N matplotlib.Table cells

    Parameters
    -----------
    table: matplotlib.Table
        the table
    cells: list[set]
        list of sets od the table coordinates
        - example: [(0,1), (0,0), (0,2)]

    Notes
    ------
    https://stackoverflow.com/a/53819765/12684122
    '''
    cells_array = [np.asarray(c) for c in cells]
    h = np.array([cells_array[i+1][0] - cells_array[i][0] for i in range(len(cells_array) - 1)])
    v = np.array([cells_array[i+1][1] - cells_array[i][1] for i in range(len(cells_array) - 1)])

    # if it's a horizontal merge, all values for `h` are 0
    if not np.any(h):
        # sort by horizontal coord
        cells = np.array(sorted(list(cells), key=lambda v: v[1]))
        edges = ['BTL'] + ['BT' for i in range(len(cells) - 2)] + ['BTR']
    elif not np.any(v):
        cells = np.array(sorted(list(cells), key=lambda h: h[0]))
        edges = ['TRL'] + ['RL' for i in range(len(cells) - 2)] + ['BRL']
    else:
        raise ValueError("Only horizontal and vertical merges allowed")

    for cell, e in zip(cells, edges):
        table[cell[0], cell[1]].visible_edges = e
        
    txts = [table[cell[0], cell[1]].get_text() for cell in cells]
    tpos = [np.array(t.get_position()) for t in txts]

    # transpose the text of the left cell
    trans = (tpos[-1] - tpos[0])/2
    # didn't had to check for ha because I only want ha='center'
    txts[0].set_transform(mpl.transforms.Affine2D().translate(*trans))
    for txt in txts[1:]:
        txt.set_visible(False)

def CreateTable(ticker, call_df, put_df, update_date):

    output_ = os.path.join(output_path, str(update_date.year), str(update_date.month).zfill(2), str(update_date.day).zfill(2))
    if not os.path.isdir(output_):
        os.makedirs(output_)
    fig = plt.figure(figsize=(7,6))
    ax=fig.gca()
    ax.axis('off')
    sub_call = call_df.reset_index()['strike,open_interest,diff'.split(',')].head(10)
    sub_put = put_df.reset_index()['strike,open_interest,diff'.split(',')].head(10)
    sub_df = pd.concat([sub_call,sub_put], axis=1)
    r,c = sub_df.shape
    # print(str(call_df.ttm.unique()[0])[2:4] + "月數據")
    # plot the real table
    table = ax.table(cellText=np.vstack([[ticker, '', update_date.strftime("%Y-%m-%d"),'', changeNumToChi(update_date.isocalendar()[-1]), ''],
                                         [str(call_df.ttm.unique()[0])[2:4] + "月數據", '', '', '', '', ''], 
                                         [int(call_df.open_interest.sum()), '', int(call_df['diff'].sum()),
                                         int(put_df.open_interest.sum()), '', int(put_df['diff'].sum())],
                                         sub_df.astype(int).values]), 
                     cellColours=[['none']*c]*(3 + r), bbox=[0, 0, 1, 1])

    table_props = table.properties()
    table_cells = table_props['children']
    for i, cell in enumerate(table_cells):
#             if not i:
#                 help(cell.set_text_props)
        cell.set_height(0.03)
        cell.set_text_props(fontproperties=ChineseFont, fontsize=12)
        text = cell.get_text().get_text()
        try:
            if int(text) < 0:
                cell.set_text_props(fontproperties=ChineseFont, fontsize=12, color='red')
        except:
            pass

    # need to draw here so the text positions are calculated
    fig.canvas.draw()

    # do the 3 cell merges needed
    mergecells(table, [(0,0), (0,1)])
    mergecells(table, [(0,2), (0,3)])
    mergecells(table, [(0,4), (0,5)])

    mergecells(table, [(1,x) for x in range(c)])

    mergecells(table, [(2,0), (2,1)])
    mergecells(table, [(2,3), (2,4)])
    
    f_path = os.path.join(output_, f'{ticker} Option OI Diff {str(call_df.ttm.unique()[0])[2:4]}.png')
    if os.path.isfile(f_path):
        os.remove(f_path)
    plt.savefig(f_path)
    plt.show(block=False)
    plt.close()

    return f_path

def changeNumToChi(weekday):
    change_dict = {
        1:"週一",
        2:"週二",
        3:"週三",
        4:"週四",
        5:"週五",
    }
    return change_dict[weekday]