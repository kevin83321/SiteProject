
from datetime import datetime, timedelta
from numpy import exp
import re
import os

call_code_list = list('ABCDEFGHIJKL')
put_code_list = list('MNOPQRSTUVWX')
call_code_map = dict((m + 1, letter) for letter, m in zip(call_code_list, range(12)))
put_code_map = dict((m + 1, letter) for letter, m in zip(put_code_list, range(12)))
opt_ticker_map = {
    'TXF':'TXO',
    'EXF':"TEO",
    'FXF':'TFO'
}

def getNextTTM(td:datetime) -> datetime:
    thirdWed = getThirdWendesday(td)
    if td.date() >= thirdWed.date():
        tmp = td + timedelta(31)
        tmp = tmp.replace(day=1)
        thirdWed = getThirdWendesday(tmp)
    return thirdWed
        
def checkClosed2TTM(td:datetime) -> bool:
    TTM = getNextTTM(td)
    diffDays = (TTM - td).days
    return diffDays <= 7

def ContractSpacing(price, ticker):
    if re.match("TXF", ticker) or re.match("TXO", ticker) or re.match("MXF", ticker):
        return 100
    if re.match("EXF", ticker) or re.match("TEO", ticker):
        if price < 150:
            return 2.5
        elif price < 500:
            return 5
        else:
            return 10
    if re.match("FXF", ticker) or re.match("TFO", ticker):
        if price < 600:
            return 10
        elif price < 2000:
            return 20
        else:
            return 40
        
def StrikeFill(strike, ticker):
    if re.match("TXF", ticker) or re.match("TXO", ticker):
        return str(strike).zfill(5)
    if re.match("EXF", ticker) or re.match("TEO", ticker):
        if int(strike) < 1000:
            return str(strike*10).zfill(5)
        else:
            return str(strike).zfill(5)
    if re.match("FXF", ticker) or re.match("TFO", ticker):
        if int(strike) < 1000:
            return str(strike*10).zfill(5)
        else:
            return str(strike).zfill(5)

def calculate_atm_strike(price, ticker, closed2TTM=False):
    spacing = ContractSpacing(price, ticker)
    if re.match("TXF", ticker) or re.match("TXO", ticker) or re.match("MXF", ticker):
        # if closed2TTM:
        #     spacing = 50
        pass
    atm = price // spacing * spacing
    if price - atm > spacing / 2:
        atm += spacing
    return int(atm), spacing
    # if re.match("EXF", ticker) or re.match("TEO", ticker):
        # quotient = int(price / spacing)
        # remainder = int(price % spacing)
        # if remainder >= spacing / 2:
        #     return (quotient + 1) * spacing, spacing
        # else:
        #     return (quotient) * spacing, spacing
    # if re.match("FXF", ticker) or re.match("TFO", ticker):
        # quotient = int(price / spacing)
        # remainder = int(price % spacing)
        # if remainder >= spacing / 2:
        #     return (quotient + 1) * spacing, spacing
        # else:
        #     return (quotient) * spacing, spacing

def ParseStrike(ticker):
    K = ticker[3:-2]
    if re.match("TEO", ticker):
        K = K[1:-1]
    elif re.match("TFO", ticker):
        K = K[1:]
    return K

def ParseStrikeTTM(ticker):
    week = 2
    if ticker[2].isnumeric():
        week = int(ticker[2]) - 1
    call_code_map = dict((letter, m + 1) for letter, m in zip(call_code_list, range(12)))
    put_code_map = dict((letter, m + 1) for letter, m in zip(put_code_list, range(12)))
    
    K = ParseStrike(ticker)    
        
    mapping_code = ticker[-2]
    y = ticker[-1]
    Y = str(datetime.today().year)[:-1] + y
    if mapping_code in call_code_list:
        M = str(call_code_map[mapping_code]).zfill(2)
        opt_type = "CALL"
    elif mapping_code in put_code_list:
        M = str(put_code_map[mapping_code]).zfill(2)
        opt_type = "PUT"
    first_day = datetime(int(Y), int(M), 2)
    if first_day.weekday() <= 2:
        adj_days = 2 - first_day.weekday()
    else:
        adj_days = 9 - first_day.weekday()
    first_wendesday = first_day + timedelta(adj_days)
    TTM = first_wendesday + timedelta(week*7) # third Wendesday
    return K, TTM, opt_type

def ParseFutTTM(ticker):
    week = 2
    if ticker[2].isnumeric():
        week = int(ticker[2]) - 1
    code_list = list('ABCDEFGHIJKL')
    code_map = dict((letter, m + 1) for letter, m in zip(code_list, range(12)))
    
    mapping_code = ticker[-2]
    M = code_map[mapping_code]
    y = ticker[-1]
    Y = str(datetime.today().year)[:-1] + y
    first_day = datetime(int(Y), int(M), 2)
    if first_day.weekday() <= 2:
        adj_days = 2 - first_day.weekday()
    else:
        adj_days = 9 - first_day.weekday()
    first_wendesday = first_day + timedelta(adj_days)
    TTM = first_wendesday + timedelta(week*7) # third Wendesday
    return TTM

def calculate_pcp(PUT, CALL, FUT, Strike, TTM_OPT, TTM_FUT=None, RiskFree=0.01, **kwargs):
    if all([PUT, CALL, FUT, Strike, TTM_OPT]):
        # return CALL + Strike * exp(-0.01/252 * TTM) - PUT - FUT * exp(-0.01/252 * TTM)
        return CALL + Strike * exp(-RiskFree * TTM_OPT) - PUT - FUT * exp(-RiskFree * (TTM_FUT if TTM_FUT else TTM_OPT))
    return float('nan')

def getNearbyCode(td:datetime):
    global call_code_map, put_code_map
    month = getNearbyMonth(td)
    return [call_code_map[month], put_code_map[month]]
    
def getNearbyMonth(td: datetime = None):
    if not td:
        td = datetime.today()
    month = td.month
    if isTimetoMaturity(td): 
        month += 1
        if month > 12:
            month = 1
    return month

def getExistsContract(date: datetime, strikes:list, symbol:str='TXF', months:int=3) -> list:
    global call_code_map, put_code_map, opt_ticker_map
    opt_ticker = opt_ticker_map[symbol]
    Conti_Ms = getExistsContractMonth(date)
    contracts = []
    y = date.year
    next_y = y + 1
    for strike in strikes:
        strike = StrikeFill(strike, symbol)
        
        for m in Conti_Ms[:months]:
            call_ticker = f'{opt_ticker}{str(strike).zfill(5)}{call_code_map[m]}{str(y)[-1]}'
            put_ticker = f'{opt_ticker}{str(strike).zfill(5)}{put_code_map[m]}{str(y)[-1]}'
            if 12 in Conti_Ms[1:3]:
                if m < 12:
                    call_ticker = f'{opt_ticker}{str(strike).zfill(5)}{call_code_map[m]}{str(next_y)[-1]}'
                    put_ticker = f'{opt_ticker}{str(strike).zfill(5)}{put_code_map[m]}{str(next_y)[-1]}'
            contracts.extend([call_ticker, put_ticker])
    return contracts

def getExistsContractMonth(date):
    month = getNearbyMonth(date)
    conti_Ms = [x if x <= 12 else x - 12 for x in range(month, month + 3)]
    if conti_Ms[-1] in [3, 4, 5]: # 3個連續月份的最後一個月是3或4或5，判斷連續季月月份，以下雷同
        conti_Ms.extend([6, 9, 12])
    elif conti_Ms[-1] in [6, 7, 8]:
        conti_Ms.extend([9, 12, 3])
    elif conti_Ms[-1] in [9, 10, 11]:
        conti_Ms.extend([12, 3, 6])
    elif conti_Ms[-1] in [12, 1, 2]:
        conti_Ms.extend([3, 6, 9])
    return conti_Ms

def isTimetoMaturity(td):
    thirdWendesday = getThirdWendesday(td)
    if td.strftime('%Y%m%d') >= thirdWendesday.strftime('%Y%m%d'): 
        return True
    return False

def getThirdWendesday(td):
    week = 2
    first_wendesday = getFirstWendesday(td)
    return first_wendesday + timedelta(week * 7)

def getFirstWendesday(td):
    first_day = datetime(td.year, td.month, 2)
    if first_day.weekday() <= 2:
        adj_days = 2 - first_day.weekday()
    else:
        adj_days = 9 - first_day.weekday()
    return first_day + timedelta(adj_days)