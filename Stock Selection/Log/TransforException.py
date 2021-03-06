# -*- encoding: UTF-8 -*-
# 實時交易模組
# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.11
# Update: 2020.02.11
# Version: 1
import linecache
import sys

def GetException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return f" In ({filename}, Line {lineno} '{line.strip()}') : {exc_obj}"

if __name__ == "__main__":
    try:
        1/0
    except:
        print(GetException())