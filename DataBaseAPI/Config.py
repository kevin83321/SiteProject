# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.06.06
# Version: Test
# !flask/bin/python

__updated__ = '2021-10-17 16:39:39'

def getConnectionConfig():
    user = 'kevin83321'
    password = 'j7629864'
    #ip = '192.168.2.191'
    ip = '192.168.2.173'
    port = 32768
    return [user, password, ip, port]

class HelpMsg:

    @staticmethod
    @property
    def ApiQuoteDailyStockHelp():
        msg = ''
        return msg

    @staticmethod
    @property
    def ApiQuoteDailyFutureHelp():
        msg = ''
        return msg