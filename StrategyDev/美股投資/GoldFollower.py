from Messenger.LineMessenger import LineMessenger as Line

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import plotly

import os
parent = os.path.dirname(os.path.abspath("__file__"))
output_path = os.path.join(parent, 'Output', 'Gold')
if not os.path.isdir(output_path):
    os.makedirs(output_path)

def getData():

    res = requests.get('https://www.spdrgoldshares.com/assets/dynamic/GLD/GLD_US_archive_EN.csv')
    res.encoding = 'utf-8'
    data = res.content.decode().split('\n')[6:]

    cols = data[0].split(', ')
    detail = data[1:]

    output = []
    for d in detail:
        try:
            if not len(d.strip()): continue
            
            tmp_d = d.split(',')
            output.append({
                cols[0]:tmp_d[0].strip(),
                cols[2]:float(tmp_d[2].replace('$','').strip()) if tmp_d[2].strip() != "HOLIDAY" else tmp_d[2].strip(),
                cols[-2]:float(tmp_d[-2].strip()) if tmp_d[-2].strip() != "HOLIDAY" else tmp_d[-2].strip(),
            })
        except:
    #         print(d, tmp_d)
            if 'NYSE' in d:
                output.append({
                    cols[0]:tmp_d[0].strip(),
                    cols[2]:float('nan'),
                    cols[-2]:float('nan'),
                })

    df = pd.DataFrame(output).set_index("Date")
    df.index = pd.to_datetime(df.index)
    col_p, col_v = df.columns

    new_ = df.resample('1w').last()

    for i in range(len(new_.index)):
        try:
            if not i:
                df.loc[df[(df.index < new_.index[i])].index[-1],'Weekly Avg V'] = df.loc[df[(df.index < new_.index[i])].index, col_v].replace("HOLIDAY",float('nan')).dropna().mean()
            else:
                df.loc[df[(df.index < new_.index[i])].index[-1],'Weekly Avg V'] = df.loc[df[(df.index > new_.index[i-1]) & (df.index < new_.index[i])].index, col_v].replace("HOLIDAY",float('nan')).dropna().mean()
        except Exception as e:
            print(e)
            if not i:
                print(df.loc[df[(df.index < new_.index[i])].index, col_v].replace("HOLIDAY",float('nan')))#.drop(0).mean())
            else:
                print(df.loc[df[(df.index > new_.index[i-1]) & (df.index < new_.index[i])].index, col_v].replace("HOLIDAY",float('nan')))#.drop(0).mean())
    return df

def PlotKBar(df, col_p, col_v, col_avg):
    
    start_date = df.index[0]
    end_date = df.index[-1]
    fig = make_subplots(
                        rows=2, cols=1, 
#                         rows=1, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0, 
                        row_width=[0.4, 0.4], # 2 rows
#                         row_width=[0.4], # 0.4, 
#                         specs=[[{"secondary_y": True}]]) # 0.2, 
                        specs=[[{"secondary_y": True}],[{"secondary_y": True}]]) # 2 rows
                        # 0.2, 
    tmp_df = df[col_v].replace("HOLIDAY",float('nan')).dropna()
#     print(tmp_df)
    fig.add_trace(
        go.Bar(x=tmp_df.index, y=tmp_df,  #fillna(method='ffill')
               showlegend=True, name = "庫存量", opacity=.3),  # "Volume"
                row=2, col=1,
    )#secondary_y= True)
    tmp_df = df[col_p].replace("HOLIDAY",float('nan')).dropna()
    fig.add_trace(
        go.Scatter(
            x=tmp_df.index,
            y=tmp_df,
            name="價格" # f"MA{ma_len}"
        ), row=1,col=1)
    
#     print(df[col_avg].replace("HOLIDAY",float('nan')).dropna())
    fig.add_trace(
        go.Scatter(
            x=df[col_avg].replace("HOLIDAY",float('nan')).dropna().index,
            y=df[col_avg].replace("HOLIDAY",float('nan')).dropna().diff(),
            name="周均量差", # f"MA{ma_len}",
            mode="markers+lines"
        ), row=2,col=1,secondary_y=True)
#     test_df = df.copy(deep=True)
#     begin_date, end_date = [start_date, end_date]
#     test_df = test_df.reindex(pd.date_range(begin_date, end_date, freq='D'))
#     datebreaks = test_df[col_p][test_df[col_p].isnull()].index
#     fig.update_xaxes(rangebreaks=[dict(values=datebreaks)])
    fig.update_layout(title_text="黃金價格與庫存量")
    f_path = os.path.join(parent, f'{end_date.strftime("%Y%m%d_Gold_Price_Inventory.jpg")}')
    fig.write_image(file=f_path, format='jpg',engine='auto')
#     fig.to_image(os.path.join(parent, f'{end_date.strftime("%Y%m%d_Gold_Price_Inventory.jpg")}'))
#     plotly.offline.plot(fig, filename=os.path.join(parent, f'{end_date.strftime("%Y%m%d_Gold_Price_Inventory.jpg")}'),auto_open=False, image='png')
    # fig.show()
    return f_path

def main():
    df = getData()
    file_path = PlotKBar(df.tail(120), *df.columns)
    Line.sendPhoto("黃金價格與庫存量更新",file_path, token='Zk6VTsmW9iN0Kh01eYPcYH09JIuG354AGDAduebBLoZ')

if __name__ == '__main__':
    main()