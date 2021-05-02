from datetime import datetime
from PySQLFunc import executeSQL, Insert, ReadSQL
from PyDBFunc import Mongo, MongoDataReader, MongoDistinct
from numpy import isnan
from FundIndicatorFunc import CalculateAllIndicators


test_sql = """SELECT TOP (1000) [PKNO]
,[UPDATE_USER_ID]
,[UPDATE_DATE]
,[UPDATE_TIME]
,[UPDATE_PROG_CD]
,[EXCHANGE]
,[ASSETS_TYPE]
,[SYMBOL_CODE]
,[DATA_YEAR]
,[DATA_SEASON]
,[ANNOUNCE_DATE]
,[FIXED_ASSETS_RATIO]
,[FIXED_ASSETS_EQUITY_RATIO]
,[FIXED_ASSETS_LONG_TERM_DEBT_RATIO]
,[FIXED_ASSETS_LONG_TERM_FUNDS_RATIO]
,[LIABILITY_RATIO]
,[LONG_TERM_FUNDS_FIXED_ASSETS_RATIO]
,[EQUITY_LIABILITY_RATIO]
,[EQUITY_LONG_TERM_DEBT_RATIO]
,[CAPITAL_TOTAL_ASSETS_REATIO]
,[NET_RATIO]
,[LONG_TERM_DET_NET_RATIO]
,[FIXED_ASSETS_NET_RATIO]
,[LEVERAGE_RATIO]
,[CURRENT_RATIO]
,[QUICK_RATIO]
,[CASH_TO_CURRENT_ASSETS_RATIO]
,[CASH_TO_CURRENT_LIABILITY_RATIO]
,[CAPITAL_TO_CURRENT_ASSETS_RATIO]
,[SHORT_TERM_BORROWING_TO_CURRENT_ASSETS_RATIO]
,[PAYABLES_TURNOVER_RATIO]
,[REVEIVABLE_TURNOVER_RATIO]
,[INVENTORY_TURNOVER_RATIO]
,[FIXED_ASSET_TURNOVER_RATIO]
,[TOTAL_ASSET_TURNOVER_RATIO]
,[NET_TURNOVER_RATIO]
,[OPERATING_INCOME_TO_CAPITAL_RATIO]
,[PRETAX_PROFIT_TO_CAPITAL_RATIO]
,[GROSS_MARGIN]
,[OPERATING_EXPENSE_RATIO]
,[OPERATING_PROFIT_RATIO]
,[PRETAX_PROFIT_MARGIN]
,[FINAL_PROFIT_MARGIN]
,[PRETAX_RETURN_ON_EQUITY]
,[AFTERTAX_RETURN_ON_EQUITY]
,[PRETAX_RETURN_ON_ASSETS]
,[AFTERTAX_RETURN_ON_ASSETS]
,[AFTERTAX_RETURN_ON_FIXED_ASSETS]
,[REVENUE_QUARTERLY_CHANGE_RATIO]
,[REVENUE_GROWTH_RATIO]
,[TOTAL_ASSET_GROWTH_RATIO]
,[NET_GROWTH_RATIO]
,[FIXED_ASSET_GROWTH_RATIO]
,[RD_EXPENSE_RATIO]
,[MANAGEMENT_EXPENSE_RATIO]
,[CASH_FLOW_RATIO]
,[BUSINESS_GROWTH_RATIO]
,[PRETAX_NET_GROWTH_RATIO]
,[AFTERTAX_NET_GROWTH_RATIO]
,[FINANCE_CREDIT_EVALUATION]
FROM [CloudInvest].[dbo].[MARKET124]"""


  
def ReadStockList():
    tb_name = 'TWSE.StockList'
    distinct_h = 'UpdateDate'
    updateDate = sorted(MongoDistinct(tb_name, distinct_h))[-1]
    condition = {
        'UpdateDate':{"$eq":updateDate},
        'AssetType':{"$eq":"股票"}
    }
    datas = MongoDataReader(tb_name, condition)
    return [d['Ticker'] for d in datas]

def get_updated_quater(tb_name):
    last_y = sorted(MongoDistinct(tb_name, "Year"))[-1]
    condition = {
        'Year':{'$eq':last_y}
    }
    datas = MongoDataReader(tb_name, condition)
    last_q = sorted([x['Quarter'] for x in MongoDataReader(tb_name, condition)])[-1]
    return [last_y, last_q]

def ReadFundmentalData(quarter):
    tickers = ReadStockList()
    tb_name = 'TWSE.Fundmental'
    condition = {
        'Ticker':{'$in':tickers},
        'Year':{'$eq':str(quarter[0])},
        'Quarter': {'$eq':str(quarter[1])},
    }
    return MongoDataReader(tb_name, condition)
    
def GetLastUpdateQuarter():
    updateDate_sql = """SELECT ALL [UPDATE_DATE] FROM [CloudInvest].[dbo].[MARKET124]"""
    UpdateDate = max([x[0] for x in ReadSQL(updateDate_sql)])
    
    temp_test_sql = test_sql + f"SELECT * FROM [CloudInvest].[dbo].[MARKET124] WHERE [CloudInvest].[dbo].[MARKET124].[UPDATE_DATE] = '{UpdateDate}'"
    last_Q = sorted(set([(x[8], x[9]) for x in ReadSQL(temp_test_sql)]))[-1]
    return last_Q

def main():
    last_quarter = GetLastUpdateQuarter() # (year, quarter)
    update_quarter = (int(last_quarter[0]), int(last_quarter[1])+1)
    if update_quarter[1] > 4:
        update_quarter = (update_quarter[0] + 1, 1)
    tickers = ReadStockList()
    last_datas = dict((x['Ticker'], x) for x in ReadFundmentalData(last_quarter))
    update_datas = dict((x['Ticker'], x) for x in ReadFundmentalData(update_quarter))
    pre_y_datas = dict((x['Ticker'], x) for x in ReadFundmentalData((update_quarter[0]-1, update_quarter[1])))
    
    results = []
    for ticker in tickers:
        results.append(CalculateAllIndicators(last_datas[ticker], 
                               update_datas[ticker],
                               pre_y_datas[ticker]))
    
if __name__ == '__main__':
    main()
    
    