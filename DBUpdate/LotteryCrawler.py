# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.28
# Update: Create
# Version: 1

__updated__ = '2021-03-13 11:30:10'

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup as bs
from Config import header
import json
from datetime import datetime
from enum import Enum
from modules import Mongo
import re

from selenium import webdriver
from selenium.webdriver.support.ui import Select
# from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
chrome = ChromeDriverManager().install()

class LotteryType(Enum):
    
    Lotto649 = '大樂透'
    Lotto638 = '威力彩'

weekday_map = {
    '0':'一',
    '1':'二',
    '2':'三',
    '3':'四',
    '4':'五',
    '5':'六',
    '6':'日',
}

def Lotto649(y=103, m=1):
    try:
        url = 'https://www.taiwanlottery.com.tw/lotto/Lotto649/history.aspx'
        
        pay_load = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': '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',
            '__VIEWSTATEGENERATOR': '11E838D2',
            '__EVENTVALIDATION': 'jA/x7p/YyP5YAFJnoyGpkVsxzTOF6tD8YuKwJtZKKwBCrn/GEVHircRjlM8/eh01yN53SsC50H9NbTQWPnPxwpAvI5J6ZblZt6Wf3pEtZO3iINhGjgnPliv4dkYkV1Jpg1Cs9I8OC2xMVZHBcBt4PKt4OOzLw4AaiG2knKToNWEi9NwS/baR1zbiJRR55HYgvdc9g57yacNzVBBaV9+MEWUlJiXJNzTWYDrLMbF8fibN4XwuOvHKu0T7BqIyseFekFZYhdVIs+TYY0P49KMeI/bzuEYsL0K6tSZ2TeHwmoLycHCqTiWpJ+8KwZrlLpYFnJ3KWc5lBV4LFDurHIu7Ub4HNwwXHmDGQ0C9sgrCp0PD0Wnn/dmCPgPZdyeac/gDKZxu1e39isivOEHKFQUJLymPY0FWfSUQzyLjXQx34ngfrUJIu/T36WPh8P3/rm2JtGd7RjeJ0rET8QWsF7aEILwboYiml6z3fWJ4n/wujcdMf9KC/RYMD63UESkAUIgMVgL5eptK1vrVOGlno7Oxfl+g2oKnqYiZpSvSyMzJ7F9/cZC8cEXRL8H260ozkNqDjfHZv/G1CXPo/Q20gKOLQGV7W/j30NlAhFMGcPlzMLgqpbrfoGyDd9C8tYxaYkszrsjzucLOJ2X0WsbYE71SdZMbk+M8AYAkUzQH9BUXiOjGwFBYJBYbNGecBQMOMa8dvqJixwrqDu/j+OdnQzRhLcCJICOo0YOkj/KNs6mIf4RZLYJnnk33uHE+Fz2pCb65ewDTbWdaqsOeJAljMGpxP3luzt4AclF41KQr8Eb/YluVbFDfjyPQzAWkFxGQVZTUBb0rzmYsNCnwjpX5/O+zGTIwApmOmhmI2tl/HOnX8dTBIPlK',
            'Lotto649Control_history$DropDownList1': '2', # 2 = 大樂透
            'Lotto649Control_history$chk': 'radYM',
            'Lotto649Control_history$dropYear': y, # Year Start with 103
            'Lotto649Control_history$dropMonth': m, # Month without zfill
            'Lotto649Control_history$btnSubmit': '查詢'
        }
        
        res = requests.post(url, headers=header, data=pay_load)
        soup = bs(res.content, 'lxml')
        tables = soup.find_all('table')
        
        final_data = []
        DrawInfoKey = []
        DrawInfoValue = []
        DrawOrder = {}
        for table in tables[2:]:
            for tr in table.find_all('tr'):
                tds = [td.text.strip() for td in tr.find_all('td')]
                if '期別' in tds:
                    DrawInfoKey = tds
                if tds[0].isnumeric() and len(tds[0]) == 9:
                    DrawInfoValue = tds
                if '順序' in tds[0]:
                    DrawOrder[tds[0]] = tds[1:]
                if '獎金分配' in tds:
                    temp_data = dict((k, v) for k, v in  zip(DrawInfoKey, DrawInfoValue))
                    temp_data['DrawOrder'] = DrawOrder
                    for k, v in temp_data.items():
                        if '開獎日' in k or '兌獎' in k:
                            temp_date = [int(x) for x in temp_data[k].split('/')]
                            temp_date[0] += 1911
                            temp_data[k] = datetime(*temp_date).strftime('%Y-%m-%d')
                    temp_data['WeekDay'] = weekday_map[str(datetime.strptime(temp_data['開獎日'], "%Y-%m-%d").weekday())]
                    final_data.append(temp_data)
                    DrawInfoKey = []
                    DrawInfoValue = []
                    DrawOrder = {}
    except:
        return []
    else:
        return final_data

def Lotto638(y=103, m=1, cnt=0): # 威力彩
    try:
        url = 'https://www.taiwanlottery.com.tw/Lotto/SuperLotto638/history.aspx'
        driver = webdriver.Chrome(chrome)
        while 1:
            try:
                driver.get(url)
                time.sleep(5)
                m_select = driver.find_element_by_css_selector('#SuperLotto638Control_history1_radYM')
                m_select.click()
                time.sleep(0.1)
                year_selection = Select(driver.find_element_by_css_selector('#SuperLotto638Control_history1_dropYear'))
                year_selection.select_by_value(str(y))
                time.sleep(0.1)
                month_selection = Select(driver.find_element_by_css_selector('#SuperLotto638Control_history1_dropMonth'))
                month_selection.select_by_value(str(m))
                time.sleep(0.1)
                search_btn = driver.find_element_by_css_selector('#SuperLotto638Control_history1_btnSubmit')
                search_btn.click()
                break
            except:
                cnt += 1
                time.sleep(15)
                if cnt >= 10:
                    break
        
        time.sleep(5)
        res = driver.page_source
        soup = bs(res, 'lxml')
        tables = soup.find_all('table')
        final_data = []
        DrawInfoKey = []
        DrawInfoValue = []
        DrawOrder = {}
        for table in tables[2:]:
            for tr in table.find_all('tr'):
                tds = [td.text.strip() for td in tr.find_all('td')]
                if '期別' in tds:
                    DrawInfoKey = tds
                if tds[0].isnumeric() and len(tds[0]) == 9:
                    DrawInfoValue = tds
                if '順序' in tds[0]:
                    DrawOrder[tds[0]] = tds[1:]
                if '獎金分配' in tds:
                    temp_data = dict((k, v) for k, v in  zip(DrawInfoKey, DrawInfoValue))
                    temp_data['DrawOrder'] = DrawOrder
                    for k, v in temp_data.items():
                        if '開獎日' in k or '兌獎' in k:
                            temp_date = [int(x) for x in temp_data[k].split('/')]
                            temp_date[0] += 1911
                            temp_data[k] = datetime(*temp_date).strftime('%Y-%m-%d')
                    temp_data['WeekDay'] = weekday_map[str(datetime.strptime(temp_data['開獎日'], "%Y-%m-%d").weekday())]
                    final_data.append(temp_data)
                    DrawInfoKey = []
                    DrawInfoValue = []
                    DrawOrder = {}
        driver.close()
    except:
        driver.close()
        if cnt <= 3:
            return Lotto638(y, m, cnt=cnt)
        return []
    else:
        return final_data

def getInfoData(lotteryType: LotteryType):
    client = Mongo()
    table = client['admin']['Lottery.Info']
    data = list(table.find({'Name':{'$eq':lotteryType.value}}))
    return data
    
def updateInfo(lotteryType: LotteryType):
    client = Mongo()
    table = client['admin']['Lottery.Info']
    data = list(table.find({'Name':{'$eq':lotteryType.value}}))
    if not data:
        temp_data = {'UpdateDate':datetime.today().strftime('%Y-%m-%d')}
        if lotteryType == LotteryType.Lotto649: # 大樂透
            temp_data.update({'Nums':[str(x).zfill(2) for x in range(1, 50)],
                            'Name':lotteryType.Lotto649.value,
                            'UpdateDate':datetime.today().strftime('%Y-%m-%d')})
        elif lotteryType == LotteryType.Lotto638: # 威力透
            temp_data.update({'Nums':{'Block1':[str(x).zfill(2) for x in range(1, 39)],
                                      'Block2':[str(x).zfill(2) for x in range(1, 9)]},
                            'Name':lotteryType.Lotto638.value,
                            'UpdateDate':datetime.today().strftime('%Y-%m-%d')})
    else:
        temp_data = data[0]
        temp_data.update({'UpdateDate':datetime.today().strftime('%Y-%m-%d')})
    table.update_one({'_id':temp_data['_id']} if '_id' in temp_data else temp_data, 
                    {'$set':temp_data}, upsert=True)
    
if __name__ == '__main__':
    # print(Lotto638(103,2))
    updateInfo(LotteryType.Lotto638)
    updateInfo(LotteryType.Lotto649)