import mysql.connector as con
import time
connection = con.connect(host='localhost',database='TW_Stock',user='root', password='root')
cursor = connection.cursor()
import os
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): path = os.getcwd()
datapath = os.path.join(path, "TWSE_Actions.txt")

import pandas as pd
start_time = time.time()
importdata = pd.read_csv(datapath, sep='\t')
duration = time.time() - start_time
print(f'read TWSE_Actions.txt use {duration} senconds')
replace = "REPLACE INTO TWSE_Actions VALUES (%s, %s, %s, %s)"
start_time = time.time()
cursor.executemany(replace,importdata.astype(str).values.tolist())
connection.commit()
duration = round((time.time() - start_time)/60, 2)
print(f'insert TWSE_Actions.txt to sql use {duration} minutes')