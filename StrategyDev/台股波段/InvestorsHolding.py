import requests
from datetime import datetime

def getInvestorsHoldings(ticker='2330'):

    url = f'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetInstitutionalInvestorsShareholding&stockId={ticker}&cmkey=8AC3KrCktONfgtX2/rN8Jg==&_=1657176944884' # 
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "Connection": "keep-alive",
    #     "Cookie": "AviviD_uuid=6f56c243-5c32-4f63-960f-803c566f9204; webuserid=ee01b649-9214-9a8f-7abb-96d05dad5a1f; AviviD_sw_version=1.0.868.210701; AviviD_tid_rmed=1; __retuid=9921f8c5-4043-6fc7-562d-af49362e7be2; __fpid=2fe7b8564b9fc8870ea293b892e675f0; AviviD_refresh_uuid_status=2; AviviD_main_uuid=null; AspSession=13pqmyfply12rjnna2mupdsa; ASP.NET_SessionId=0b1smgbe2xtxbfm5eazvlbfk; _gid=GA1.2.681745620.1657175926; __asc=872cd216181d761e55e47f1a06a; __auc=872cd216181d761e55e47f1a06a; _fbp=fb.1.1657175926589.2078579904; __gads=ID=7ffc755411533e32:T=1657175928:S=ALNI_MazzQmew47edbM1xhozBzPgzlEpgA; __gpi=UID=0000077089fd2ef9:T=1657175928:RT=1657175928:S=ALNI_MZX3eGwOrZNkFLWw-1mjGlcW_FFQQ; AviviD_already_exist=1; AviviD_show_sub=1; AviviD_waterfall_status=0; AviviD_token_retake=0; _gat_UA-30929682-4=1; _gat_UA-30929682-1=1; _gat_real=1; page_view=3; _ga=GA1.2.1647502330.1657175926; _ga_6P4X22LDKK=GS1.1.1657175925.1.1.1657175994.0; _ga_SG15L0JFQ7=GS1.1.1657175925.1.1.1657175994.53; _ga_LNLNZDREEJ=GS1.1.1657175925.1.1.1657175994.0",
    #     "Host": "www.cmoney.tw",
        "Referer": f"https://www.cmoney.tw/finance/{ticker}/f00036",
    #     "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    #     "sec-ch-ua-mobile": "?0",
    #     "sec-ch-ua-platform": '"Windows"',
    #     "Sec-Fetch-Dest": "empty",
    #     "Sec-Fetch-Mode": "cors",
    #     "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    pay_load = {
        "action": "GetInstitutionalInvestorsShareholding",
        "stockId": ticker,
        "cmkey": "8AC3KrCktONfgtX2/rN8Jg=="
    }
    return requests.get(url, headers=headers, data=pay_load)

def getInfo(ticker='2330'):

    url = f'https://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetStockBasicInfo&stockId={ticker}&cmkey=yDW3Gc6baoRY%2B7JKrCgMfQ==' # 
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    #     "Connection": "keep-alive",
    #     "Cookie": "AviviD_uuid=6f56c243-5c32-4f63-960f-803c566f9204; webuserid=ee01b649-9214-9a8f-7abb-96d05dad5a1f; AviviD_sw_version=1.0.868.210701; AviviD_tid_rmed=1; __retuid=9921f8c5-4043-6fc7-562d-af49362e7be2; __fpid=2fe7b8564b9fc8870ea293b892e675f0; AviviD_refresh_uuid_status=2; AviviD_main_uuid=null; AspSession=13pqmyfply12rjnna2mupdsa; ASP.NET_SessionId=0b1smgbe2xtxbfm5eazvlbfk; _gid=GA1.2.681745620.1657175926; __asc=872cd216181d761e55e47f1a06a; __auc=872cd216181d761e55e47f1a06a; _fbp=fb.1.1657175926589.2078579904; __gads=ID=7ffc755411533e32:T=1657175928:S=ALNI_MazzQmew47edbM1xhozBzPgzlEpgA; __gpi=UID=0000077089fd2ef9:T=1657175928:RT=1657175928:S=ALNI_MZX3eGwOrZNkFLWw-1mjGlcW_FFQQ; AviviD_already_exist=1; AviviD_show_sub=1; AviviD_waterfall_status=0; AviviD_token_retake=0; _gat_UA-30929682-4=1; _gat_UA-30929682-1=1; _gat_real=1; page_view=3; _ga=GA1.2.1647502330.1657175926; _ga_6P4X22LDKK=GS1.1.1657175925.1.1.1657175994.0; _ga_SG15L0JFQ7=GS1.1.1657175925.1.1.1657175994.53; _ga_LNLNZDREEJ=GS1.1.1657175925.1.1.1657175994.0",
    #     "Host": "www.cmoney.tw",
        "Referer": f"https://www.cmoney.tw/finance/{ticker}/f00026",
    #     "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    #     "sec-ch-ua-mobile": "?0",
    #     "sec-ch-ua-platform": '"Windows"',
    #     "Sec-Fetch-Dest": "empty",
    #     "Sec-Fetch-Mode": "cors",
    #     "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    pay_load = {
        "action": "GetInstitutionalInvestorsShareholding",
        "stockId": ticker,
        "cmkey": "yDW3Gc6baoRY%2B7JKrCgMfQ=="
    }
    return requests.get(url, headers=headers, data=pay_load)

def getInvestorHolding(ticker, date = datetime.today()):
    output = {}
    res_Investors = getInvestorsHoldings(ticker)
    data_Investors = res_Investors.join()
    if data_Investors[0]['Date'] != date.strftime("%Y%m%d"):
        return output
    InvestmentTrustShareholdingRate = float(data_Investors['InvestmentTrustShareholdingRate']) # 投信持股比例
    ForeignInvestorsShareholdingRate = float(data_Investors['ForeignInvestorsShareholdingRate']) # 外資持股比例

    ForeignInvestorsBuySell = float(data_Investors['ForeignInvestorsBuySell']) # 外資買賣超
    InvestmentTrustBuySell = float(data_Investors['InvestmentTrustBuySell']) # 投信買賣超
    
    res_info = getInfo()
    data_info = res_info.json()
    outstanding = float(data_info['PaidInCapital']) * 1e6 / 10

    output = {
        "外資持股比例":ForeignInvestorsShareholdingRate,
        "外本比":ForeignInvestorsBuySell / outstanding,
        "投信持股比例":InvestmentTrustShareholdingRate,
        "投本比":InvestmentTrustBuySell / outstanding
    }
    return output