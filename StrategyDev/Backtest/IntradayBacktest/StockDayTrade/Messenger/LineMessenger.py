# -*- encoding: UTF-8 -*-
# Line Messenger
# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.17
# Update: 2020.02.17
# Version: 1

import requests

class LineMessenger:

    @staticmethod
    def sendPhoto(msg, picURI, token="YgIEWKYHSFjVtB86HSU8frRQDA0rXnZ7CF9rtXcRM7v"):
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization":"Bearer "+token}
        payload = {'message': msg}
        files = {'imageFile': open(picURI, 'rb')}
        r = requests.post(url, headers = headers, params = payload, files = files)
        #return r.status_code

    @staticmethod
    def sendMessage(msg, msg2='', msg3=''):
        """
        傳訊息至Line Notify
        """
        url = "https://maker.ifttt.com/trigger/ServerInformation/with/key/bmsGx8rqE3pk6bRBGhRO_k"
        requests.post(url, data={'value1':str(msg), 'value2':str(msg2),'value3':str(msg3)})

    @staticmethod
    def sendDocument(msg, filepath, token="YgIEWKYHSFjVtB86HSU8frRQDA0rXnZ7CF9rtXcRM7v"):
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization":"Bearer "+token}
        payload = {'message': msg}
        files = {'Document': open(filepath, 'rb')}
        r = requests.post(url, headers = headers, params = payload, files = files)