import json
from pymongo import MongoClient
import os
from itertools import product

parent = os.path.dirname(os.path.abspath(__file__))
filledPath = os.path.join(parent, 'filled_data')
if not os.path.isdir(filledPath):
    os.makedirs(filledPath)

if __name__ == '__main__':
    db_name = 'TWSE.Fundmental'
    
    myclient = MongoClient('mongodb://kevin:j7629864@localhost:27017')
    myschema = myclient['admin']
    mydb = myschema[db_name]
    
    client = MongoClient('mongodb://xiqi:xiqi2018@220.135.204.227:27017')
    schema = client['admin']
    dbs = schema.list_collection_names()
    db = schema[db_name]
    first_create = db_name not in dbs
    first_create = db.count() == 0
    if first_create:
        db.create_index([('Ticker', 1), ('Year', 1), ('Quarter', 1)])
        # insert_db_first_time(db)
    
    for year, season in product(range(2013,2021), range(1,5)):
        targetPath = os.path.join(filledPath, f'{year}Q{season}')
        # listFiles = os.listdir(targetPath)
        # for filename in listFiles:
        try:
            temp = list(mydb.find({'Year':{'$eq':str(year)}, 'Quarter':{'$eq':str(season)}}))
            for x in temp: del x['_id']
            # print(temp)
            db.insert_many(temp)
            print(f'Finish {year}Q{season}')
        except Exception as e:
            print(e)
            pass
