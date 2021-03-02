# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.28
# Update: Create
# Version: 1

__updated__ = '2021-03-02 00:41:45'

import time
from modules import Tele, Mongo
import json
from datetime import datetime

from LotteryCrawler import Lotto649, updateInfo, LotteryType, getInfoData

def UpdateLotto649():
    client = Mongo()
    table = client['admin']['Lottery.Draw.Lotto649']
    cnt = table.count_documents({})
    final_data = []
    if not cnt: # insert first time
        # fill old data
        table.create_index([('期別', 1), ('開獎日', 1)], unique=True)
        for y in range(103, datetime.today().year):
            for m in range(1, 13):
                final_data.extend(Lotto649(y, m))
                time.sleep(5)
        # fill current year data
        td = datetime.today()
        y = td.year
        for m in range(1, td.month + 1):
            final_data.extend(Lotto649(y, m))
    else: # Daily Update
        td = datetime.today()
        y = td.year
        m = td.month
        final_data.extend(Lotto649(y, m))
        time.sleep(5)
    info = getInfoData(LotteryType.Lotto649)
    if not info:
        table.insert_many(final_data)
    else:
        final_data = [x for x in final_data if x['開獎日'] > info[0]['UpdateDate']]
        table.insert_many(final_data)
    # Update Information
    updateInfo(LotteryType.Lotto649)
    

if __name__ == '__main__':
    UpdateLotto649()