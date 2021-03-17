# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.28
# Update: Create
# Version: 1

__updated__ = '2021-03-13 11:41:07'

import time
from modules import Tele, Mongo
import json
from datetime import datetime

from LotteryCrawler import Lotto649, updateInfo, LotteryType, getInfoData, Lotto638

def UpdateLotto649():
    client = Mongo()
    table = client['admin']['Lottery.Draw.Lotto649']
    cnt = table.count_documents({})
    if not cnt: # insert first time
        # fill old data
        table.create_index([('期別', 1), ('開獎日', 1)], unique=True)
        for y in range(103, datetime.today().year):
            for m in range(1, 13):
                i = 0
                while i < 3:
                    final_data = Lotto649(y, m)                    
                    if final_data:
                        table.insert_many(final_data)
                        final_data = []
                        break
                    time.sleep(5)
                    i += 1
                time.sleep(15)
        # fill current year data
        td = datetime.today()
        y = td.year
        for m in range(1, td.month + 1):
            i = 0
            while i < 3:
                final_data = Lotto649(y, m)                    
                if final_data:
                    table.insert_many(final_data)
                    final_data = []
                    break
                time.sleep(5)
                i += 1
    else: # Daily Update
        td = datetime.today()
        y = td.year
        m = td.month
        i = 0
        while i < 3:
            final_data = Lotto649(y, m)                    
            if final_data:
                break
            time.sleep(5)
            i += 1
        # time.sleep(5)
        info = getInfoData(LotteryType.Lotto649)
        if not info:
            if final_data:
                table.insert_many(final_data)
        else:
            final_data = [x for x in final_data if x['開獎日'] > info[0]['UpdateDate']]
            if final_data:
                table.insert_many(final_data)
    # Update Information
    updateInfo(LotteryType.Lotto649)
    
def UpdateLotto638():
    client = Mongo()
    table = client['admin']['Lottery.Draw.Lotto638']
    cnt = table.count_documents({})
    if not cnt: # insert first time
        # fill old data
        table.create_index([('期別', 1), ('開獎日', 1)], unique=True)
        for y in range(103, datetime.today().year):
            for m in range(1, 13):
                print(y, m)
                i = 0
                while i < 3:
                    final_data = Lotto638(y, m)
                    if final_data:
                        print(final_data)
                        table.insert_many(final_data)
                        final_data = []
                        break
                    time.sleep(5)
                    i += 1
                time.sleep(15)
        # fill current year data
        td = datetime.today()
        y = td.year
        for m in range(1, td.month + 1):
            i = 0
            while i < 3:
                final_data = Lotto638(y, m)                    
                if final_data:
                    table.insert_many(final_data)
                    final_data = []
                    break
                time.sleep(5)
    else: # Daily Update
        td = datetime.today()
        y = td.year
        m = td.month
        i = 0
        while i < 3:
            final_data = Lotto638(y, m)                    
            if final_data:
                break
            i += 1
            time.sleep(5)
        # time.sleep(5)
        info = getInfoData(LotteryType.Lotto638)
        if not info:
            if final_data:
                table.insert_many(final_data)
        else:
            final_data = [x for x in final_data if x['開獎日'] > info[0]['UpdateDate']]
            if final_data:
                table.insert_many(final_data)
    # Update Information
    updateInfo(LotteryType.Lotto638)
    

if __name__ == '__main__':
    UpdateLotto649()
    UpdateLotto638()