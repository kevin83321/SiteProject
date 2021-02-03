import pandas as pd
import os, time
from modules import Mongo, Tele
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): 
    path = os.getcwd()
    
__updated__ = '2021-01-30 18:32:50'

if __name__ == '__main__':
    client = Mongo()
    table = client['admin']['TWSE']['Actions']
    table.create_index([('Date', 1), ('Ticker', 1), ('Action', 1)], unique=True)
    df = pd.read_csv(os.path.join(path, 'TWSE_Actions.txt'), sep='\t')
    data = [dict(x._asdict().items()) for x in df.itertuples()]
    for d in data: del d['Index']
    start_time = time.time()
    table.insert_many(data)
    duration = round((time.time() - start_time) / 60, 4)
    Tele().sendMessage(f'insert {len(data)} data use {duration} mins', group='UpdateMessage')