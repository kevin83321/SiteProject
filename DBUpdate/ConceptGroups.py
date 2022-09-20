import requests
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
from modules import Tele, Mongo
from Log.TransforException import TransforException

def getConceptGroup():
    class_url = "https://tw.stock.yahoo.com/class/"
    res = requests.get(class_url)
    soup = bs(res.content, 'lxml')

    concept_groups = soup.find_all('div', {'id':'CONCEPT_STOCK'})
    groups = {}
    for concept_g in concept_groups[0].find_all('div')[2:]:
        tmp_input = concept_g.find_all('a')[0].get('href')
        tmp_input = tmp_input[tmp_input.index('?')+1:].split('&')
        groups[concept_g.text] = dict((value.split('=')[0], value.split('=')[1]) for value in tmp_input)
#         groups[concept_g.text]['PRID'] = getPRID(groups, concept_g.text)
#         time.sleep(3)
    return groups

def getPRID(group, key):
    try:
        category = key
        categoryLabel = group[key]['categoryLabel']
        stocks_url = f'https://tw.stock.yahoo.com/class-quote?category={key}&categoryLabel={categoryLabel}'
        res_stock = requests.get(stocks_url)
        stock_soup = bs(res_stock.content, 'lxml')
        tmp_text = str(stock_soup)[str(stock_soup).index('"prid"'):]
        tmp_text = tmp_text[:tmp_text.index(',')]
    except:
        print(key)
        print(stock_soup)
    else:
        return tmp_text.split(':')[1].replace('\"', '')

def getGroupStocks(conceptGroup):
    stock_url = 'https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;category={0};categoryLabel={1};categoryName={0};offset={2}?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseNewQuoteTabColor&intl=tw&lang=zh-Hant-TW&partner=none&prid={3}&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1466&returnMeta=true'
    offset = 0
    output = {}
    for k, v in conceptGroup.items():
        output[k] = output.get(k, [])
        while offset >= 0:
            url_ = stock_url.format(v['category'], v['categoryLabel'], offset, '') # v['PRID'] if v['PRID'] else 
            res_ = requests.get(url_)
            output[k] += res_.json()['data']['list']
            if res_.json()['data']['pagination']['nextOffset']:
                offset = int(res_.json()['data']['pagination']['nextOffset'])
            else:
                offset = 0
                break
            time.sleep(3)
    return output
        
def update_one(table, d):
    try:
        table.update_one(d, {'$set':d}, upsert=True)
    except Exception as e:
        print(TransforException.GetException())

def update_db(table, datas):
    try:
        table.insert_many(datas)
    except:
        for d in datas:
            update_one(table, d)

def main():
    ########################
    # Setup database
    ########################
    
    # Connect to Mongo
    client = Mongo()
    schema = client['admin']
    collections = schema.collection_names()
    table_name = 'ConceptGroups'
    td = datetime.today()
    first_time = False
    
    # Setup Interday Future DB
    table = schema[table_name]
    first_time = table_name not in collections
    # cnt = schema[table_name].count()
    if first_time: # if db not exist or db is empty
        table.create_index([('UpdateDate',1), ('Ticker', 1), ('Group', 1)])

    ##################################
    # Get Data From Yahoo Finance (TW)
    ##################################
    conceptGroup = getConceptGroup()
    output = getGroupStocks(conceptGroup)

    output_data = []
    for g_name, stocks in output.items():
        for d in stocks:
            output_data.append({
                "UpdateDate":td.strftime("%Y-%m-%d"),
                "Ticker":d['symbol'].split('.')[0],
                "Name":d['symbolName'],
                "Market": "TWSE" if d['exchange'] == 'TAI' else "OTC",
                "sectorName":d['sectorName'],
                "Group":g_name
            })
    ##################################
    # Update to Mongo
    ##################################
    update_db(table, output_data)

if __name__ == '__main__':
    main()
