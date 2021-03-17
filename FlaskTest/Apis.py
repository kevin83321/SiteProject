import pandas as pd
import os
import json
parent = os.path.dirname(os.path.abspath(__file__))

cols = 'FUT_Ticker,FullName,STC_Ticker,ShortName,HasFut,HasOpt,IsList,IsOTC,IsETF,Multiplier'.split(',')
cht_col = '期貨代號,公司全名,股票代號,公司簡稱,有期貨,有選擇權,上市股票,上櫃股票,ETF,對應股數'.split(',')
col_map = dict((col, cht) for col, cht in zip(cols, cht_col))

def CreateJsonFile():
    df = pd.read_excel(os.path.join(parent, '2_stockinfo.xls'), skiprows=2)[:-2]
    df.columns = cols
    df.loc[141, 'FUT_Ticker'] = 'NA'
    df['STC_Ticker'] = df['STC_Ticker'].apply(lambda x: str(int(x)))
    datas = []
    for temp_d in df.T.to_dict().values():
        if isinstance(temp_d['IsETF'], str):
            temp_d['STC_Ticker'] = '00' + temp_d['STC_Ticker']
        datas.append(temp_d)
    if not os.path.isfile(os.path.join(parent, 'STC_FUT.json')):
        with open(os.path.join(parent, 'STC_FUT.json'), 'w') as f:
            json.dump(datas,f)
            
def ReadJson():
    if not os.path.isfile(os.path.join(parent, 'STC_FUT.json')):
        CreateJsonFile()
    with open(os.path.join(parent, 'STC_FUT.json'), 'r') as f:
        return json.load(f)
    
if __name__ == '__main__':
    CreateJsonFile()