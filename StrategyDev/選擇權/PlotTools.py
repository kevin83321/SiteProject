import matplotlib as mpl
import matplotlib.pyplot as plt
from Utils import os, output_path, np
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

def CreateTable(output):

    output_ = os.path.join(output_path, "Summary", "Fig")
    if not os.path.isdir(output_):
        os.makedirs(output_)
    size_m = 1.2
    fig = plt.figure(figsize=(6.4*size_m,4.8*size_m), dpi=300)
    ax=fig.gca()
    ax.axis('off')
    r_n, c_n = 13, 10#sub_df.shape
    call_oi = output['買權']
    put_oi = output['賣權']
    k = "履約價"
    v = "口數"
    c = '買權'
    p = "賣權"
    insti = "三大法人_未平倉"
    large = '十大_未平倉'
    row1 = ['日期', '', output['日期'], '未平倉', '', '', '', '三大法人', '', '']
    row2 = ['現貨收盤價', '', output['現貨收盤價'], '', '', '履約價', '口數', '', '買權', '賣權']
    row3 = ['期貨收盤價', '', output['期貨收盤價'], '買權', '最大\n未平倉', call_oi['最大未平倉'][k], call_oi['最大未平倉'][v], '自營', output[insti]['自營商'][c], output[insti]['自營商'][p]]
    row4 = ['P/C Ratio', '', output['P/C Ratio'], '', '未平倉\n最大增幅', call_oi['未平倉最大增幅'][k], call_oi['未平倉最大增幅'][v], '投信', output[insti]['投信'][c], output[insti]['投信'][p]]
    row5 = ['買權隱波', '價內', output['買權隱波-價內'], '', '未平倉\n最大減幅', call_oi['未平倉最大減幅'][k], call_oi['未平倉最大減幅'][v], '外資', output[insti]['外資'][c], output[insti]['外資'][p]]
    row6 = ['', '價平', output['買權隱波-價平'], '', '價平\n增減幅', call_oi['價平增減幅'][k], call_oi['價平增減幅'][v], '十大交易人', '', '']
    row7 = ['', '價外', output['買權隱波-價外'], '', '價內\n最大增幅', call_oi['價內最大增幅'][k], call_oi['價內最大增幅'][v], '', '買權', '賣權']
    row8 = ['賣權隱波', '價內', output['賣權隱波-價內'], '賣權', '最大\n未平倉', put_oi['最大未平倉'][k], put_oi['最大未平倉'][v], '交易人(近)', output[large]['交易人']['近月'][c], output[large]['交易人']['近月'][p]]
    row9 = ['', '價平', output['賣權隱波-價平'], '', '未平倉\n最大增幅', put_oi['未平倉最大增幅'][k], put_oi['未平倉最大增幅'][v], '交易人(全)', output[large]['交易人']['全月'][c], output[large]['交易人']['全月'][p]]
    row10 = ['', '價外', output['賣權隱波-價外'], '', '未平倉\n最大減幅', put_oi['未平倉最大減幅'][k], put_oi['未平倉最大減幅'][v], '特法(近)', output[large]['特法']['近月'][c], output[large]['特法']['近月'][p]]
    row11 = ['歷史波動率', '20天', output['歷史波動率_20天'], '', '價平\n增減幅', put_oi['價平增減幅'][k], put_oi['價平增減幅'][v], '特法(全)', output[large]['特法']['全月'][c], output[large]['特法']['全月'][p]]
    row12 = ['', '60天', output['歷史波動率_60天'], '', '價內\n最大增幅', put_oi['價內最大增幅'][k], put_oi['價內最大增幅'][v], '', '', '']
    row13 = ['', '260天', output['歷史波動率_260天'], '', '', '', '', '', '', '']
    # plot the real table
    table = ax.table(cellText=np.vstack([row1, row2, row3,
                                         row4, row5, row6,
                                         row7, row8, row9,
                                         row10, row11, row12,
                                         row13,
                                         ]), 
                     cellColours=[['none']*c_n]*(r_n), bbox=[0, 0, 1, 1])

    table_props = table.properties()
    table_cells = table_props['children']
    f_size = 60
    for i, cell in enumerate(table_cells):
        cell.set_height(0.01)
        cell.set_text_props(fontproperties=ChineseFont, fontsize=f_size)
        text = cell.get_text().get_text()
        try:
            if int(text) < 0:
                cell.set_text_props(fontproperties=ChineseFont, fontsize=f_size, color='red')
        except:
            pass

    # need to draw here so the text positions are calculated
    fig.canvas.draw()

    # do the 3 cell merges needed
    mergecells(table, [(0,0), (0,1)]) # 日期
    mergecells(table, [(1,0), (1,1)]) # 現貨收盤
    mergecells(table, [(2,0), (2,1)]) # 期貨收盤
    mergecells(table, [(3,0), (3,1)]) # P/C Ratio
#     mergecells(table, [(4,0), (6,0)]) # 買權隱波
#     mergecells(table, [(7,0), (9,0)]) # 賣權隱波
#     mergecells(table, [(10,0), (12,0)]) # 歷史波
    
    mergecells(table, [(0,3), (0,6)]) # 未平倉
#     mergecells(table, [(2,3), (6,3)]) # 買權
#     mergecells(table, [(7,3), (11,3)]) # 賣權
    
    mergecells(table, [(0,7), (0,9)]) # 三大法人
    mergecells(table, [(5,7), (5,9)]) # 十大
    
    f_path = os.path.join(output_, f'{output["日期"]} TXO Daily Info .png')
    if os.path.isfile(f_path):
        os.remove(f_path)
    plt.savefig(f_path)
    plt.show(block=False)
#     plt.close()

    return f_path