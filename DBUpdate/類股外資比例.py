from pandas import date_range
from datetime import datetime, timedelta
import time
from modules import Tele, Mongo, crawl_json_data

col_map = {
        '產業別':'Industry',
        '家數':'NumofIndustry',
        '總發行股數':'TotalShares',
        '僑外資及陸資持有總股數':'HoldingShares',
        '僑外資及陸資持股比率':'HoldingPercentage',
    }

def changeType(k, v):
    k = col_map[k]
    if k in 'NumofIndustry,TotalShares,HoldingShares'.split(','):
        v = float(str(v).replace(',', ''))
    return (k, v)

def crawl_foriegn_holding_ratio_otc(date):
    full_df = []
    cols = '產業別,家數,總發行股數,僑外資及陸資持有總股數,僑外資及陸資持股比率'.split(',')
    try:
        dateStr = '/'.join([str(date.year - 1911), date.strftime('%m/%d')])
        js = crawl_json_data(f'https://www.tpex.org.tw/web/stock/3insti/qfii_sect/qfiisect_result.php?l=zh-tw&_=1606059780282&o=json&d={dateStr}')
        data = js['aaData']
        for ds in data:
            temp_dict = dict(changeType(col, d) for col, d in zip(cols, ds))
            temp_dict['Date'] = date.strftime('%Y-%m-%d')
            full_df.append(temp_dict)
        time.sleep(10)
    except Exception as e:
        print(e)
        time.sleep(10)
    else:
        return full_df

def crawl_foriegn_holding_ratio_listed(date):
    full_df = []
    cols = None
    try:
        dateStr = date.strftime('%Y%m%d')
        js = crawl_json_data(f'https://www.twse.com.tw/fund/MI_QFIIS_cat?response=json&date={dateStr}')
        cols = js['fields']
        data = js['data']
        for ds in data:
            temp_dict = dict(changeType(col, d) for col, d in zip(cols, ds))
            temp_dict['Date'] = date.strftime('%Y-%m-%d')
            full_df.append(temp_dict)
        time.sleep(10)
    
    except Exception as e:
        print(e)
        time.sleep(10)
    else:
        return full_df
    
def crawl_listed(schema):
    table_name = 'TWSE.ForeignInvestment.Industry'
    collections = schema.list_collection_names()
    table = schema[table_name]
    if table_name not in collections:        
        table.create_index([('Date',1), ('Industry',1)])
        start = datetime(2000,12,7)
    else:
        start = datetime.strptime(sorted(table.distince('Date'))[-1], "%Y-%m-%d") + timedelta(1)
    
    td = datetime.today()
    dates = date_range(start, td)
    for date in dates:
        full_data = crawl_foriegn_holding_ratio_listed(date)
        if full_data:
            table.insert_many(full_data)
        # Tele().sendMessage(f'爬取 {date.strftime("%Y-%m-%d")} 上市類股外資持股比例成功')
            
def crawl_otc(schema):
    table_name = 'TWSE.ForeignInvestment.Industry.OTC'
    collections = schema.list_collection_names()
    table = schema[table_name]
    if table_name not in collections:
        table.create_index([('Date',1), ('Industry',1)])
        start = datetime(2007,4,23)
    else:
        cnt = table.count_documents({})
        if cnt == 0:
            start = datetime(2007,4,23)
        else:
            start = datetime.strptime(sorted(table.distinct('Date'))[-1], "%Y-%m-%d") + timedelta(1)
    
    td = datetime.today()
    dates = date_range(start, td)
    for date in dates:
        full_data = crawl_foriegn_holding_ratio_otc(date)
        if full_data:
            table.insert_many(full_data)
        # Tele().sendMessage(f'爬取 {date.strftime("%Y-%m-%d")} 上櫃類股外資持股比例成功')

if __name__ == '__main__':
    client = Mongo()
    schema = client['admin']
    # crawl_listed(schema)
    crawl_otc(schema)    
    Tele().sendMessage(f'爬取外資持股比例成功', group='UpdateMessage')