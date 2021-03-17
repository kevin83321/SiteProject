from UpdateOTCData import getOTCList
from datetime import datetime
from PySQLFunc import executeSQL, GetPKNO, Insert
from numpy import isnan

def changeIntoSQLForm(data):
    td = datetime.today()
    d, t = td.strftime('%Y/%m/%d %H:%M:%S').split(' ')
    return {
        'UPDATE_USER_ID':"'Kevin'",
        'UPDATE_DATE':f"'{d}'",
        'UPDATE_TIME':f"'{t}'",
        'UPDATE_PROG_CD':"''", 
        'EXCHANGE':"'TW'", 
        'ASSETS_TYPE':"'STOCK'" if data['AssetType'] == '股票' else f"'{data['AssetType']}'", #data['AssetType'] 
        'SYMBOL_CODE':f"'{data['Ticker']}'", 
        'SYMBOL_ATTR':"'OTC'", 
        'SYMBOL_NAME':f"'{data['Name']}'", 
        'IS_ORDER':1, 
        'PUBLIC_DATE':f"'{data['IssueDate'].replace('-', '/')}'"
    }
    
def changeNaN(x):
    pass

def OTCInfo():
    datas, _, updateDate = getOTCList()
    datas = [changeIntoSQLForm(x) for x in datas]
    return datas
    
def InsertSQLInfo(datas):
    temp_k = None
    for data in datas:
        if not temp_k:
            temp_k = list(data.keys())
            k_str = ', '.join(temp_k)
        v_str = ', '.join([str(data[k]) for k in temp_k])
        Insert(db = 'MAEKET101', k_str=k_str, v_str=v_str)        
    
if __name__ == '__main__':
    datas = OTCInfo()
    InsertSQLInfo(datas)