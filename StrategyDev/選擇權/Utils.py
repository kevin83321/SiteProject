import requests
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
import os
from modules import Mongo
import json

parent = os.path.dirname(os.path.abspath("__file__"))
output_path = os.path.join(parent, "Output")
if not os.path.isdir(output_path):
    os.makedirs(output_path)

eng2chi = {"Call":"買權", "Put":"賣權"}

def checkPath(pth):
    if not os.path.isdir(pth):
        os.makedirs(pth)

def Connect2Mongo(table_name = 'TWSE.HistoricalPrice.Index.Interday'):
    client = Mongo()
    schema = client['admin']
    return schema[table_name]