# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.06.06
# Update: 2020.06.06
# Version: Test
# !flask/bin/python

def getConnectionConfig():
    user = 'kevin'
    password = 'j7629864'
    ip = '192.168.2.191'
    port = 27071
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