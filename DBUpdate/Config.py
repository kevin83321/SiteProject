# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.06.06
# Update: add header
# Version: Test
# !flask/bin/python

__updated__ = '2021-06-09 00:31:54'

def getConnectionConfig():
    user = 'kevin83321'
    password = 'j7629864'
    ip = '192.168.2.173'
    # ip = '192.168.0.10'
    port = 49153 # 32768
    return [user, password, ip, port]

header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'upgrade-insecure-requests': '1'}

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