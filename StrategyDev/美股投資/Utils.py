import requests
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
import os

parent = os.path.dirname(os.path.abspath("__file__"))
output_path = os.path.join(parent, "Output")
if not os.path.isdir(output_path):
    os.makedirs(output_path)