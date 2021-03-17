# -*- encoding: UTF-8 -*-
# CopyRight© : WinTog
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.03.04
# Update: Create
# Version: 1

__updated__ = '2021-03-06 11:41:54'

from PyDBFunc import SQLServer

cnxn, cursor = SQLServer()

def executeSQL(sql):
    # Do the insert
    cursor.execute(sql)
    
    
def Insert(db = 'MAEKET101', k_str='', v_str=''):
    try:
        sql = f"""INSERT INTO [CloudInvest].[dbo].[MARKET101]
                ({k_str})
                VALUES 
                ({v_str})"""
        executeSQL(sql)
        #commit the transaction
        cnxn.commit()
    except Exception as e:
        print(e)

def GetPKNO(db='MARKET101'):
    sql = f"""SELECT ALL [PKNO] FROM [CloudInvest].[dbo].[{db}]"""
    datas = ReadSQL(sql)
    return sorted(datas, key=lambda x: x[0])[-1][0]

def ReadSQL(sql, batch_size=100):
    #     sql='''SELECT TOP (1000) [PKNO]
    #       ,[UPDATE_USER_ID]
    #       ,[UPDATE_DATE]
    #       ,[UPDATE_TIME]
    #       ,[UPDATE_PROG_CD]
    #       ,[EXCHANGE]
    #       ,[ASSETS_TYPE]
    #       ,[SYMBOL_CODE]
    #       ,[SYMBOL_ATTR]
    #       ,[SYMBOL_NAME]
    #       ,[IS_ORDER]
    #       ,[PUBLIC_DATE]
    #   FROM [CloudInvest].[dbo].[MARKET101]'''
    
    executeSQL(sql)
    row = cursor.fetchmany(batch_size)
    final_datas = []
    while 1:
        if row:
            final_datas.append(row.pop(0))
            if not row:
                row = cursor.fetchmany(batch_size)
        if not row:
            break
    return final_datas

def DeleteSQL():
    sql=''
    executeSQL(sql)
    
    
if __name__ == '__main__':
    GetPKNO()