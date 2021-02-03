import pandas as pd
import os, time
from modules import Tele, Mongo
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): 
    path = os.getcwd()
    
__updated__ = '2021-01-31 04:21:20'

if __name__ == '__main__':
    client = Mongo()
    _batch_size = 15 * 1024 * 1024

    table = client['admin']['USSE']['historicalPrice']
    table.create_index([('Date',1), ('Ticker',1)], unique=True)

    start_time = time.time()
    datas = pd.read_csv(os.path.join(path, 'USSE_HistoricalPrice.txt'), sep='\t', chunksize=_batch_size)
    total_data = 0
    for df in datas:
        data = [dict(x._asdict().items()) for x in df.itertuples()]
        for d in data: del d['Index']
        table.insert_many(data)
        total_data += len(data)
    duration = round((time.time() - start_time) / 60, 4)
    Tele().sendMessage(f'insert {total_data} USSE Historical data use {duration} mins', group='UpdateMessage')