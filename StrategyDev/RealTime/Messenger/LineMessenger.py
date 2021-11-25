# -*- encoding: UTF-8 -*-
# Line Messenger
# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.17
# Update: 2020.02.17
# Version: 1

import requests
import configparser
import os
parent = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(parent):
    parent = os.getcwd()

class LineMessenger:

    @staticmethod
    def sendPhoto(msg, picURI, token="YgIEWKYHSFjVtB86HSU8frRQDA0rXnZ7CF9rtXcRM7v"):
        try:
            url = "https://notify-api.line.me/api/notify"
            headers = {"Authorization":"Bearer "+token}
            payload = {'message': msg}
            files = {'imageFile': open(picURI, 'rb')}
            r = requests.post(url, headers = headers, params = payload, files = files)
            print(r.status_code)
        except Exception as e:
            print(e)
        #return r.status_code

    # @staticmethod
    # def sendMessage(msg, msg2='', msg3=''):
    #     """
    #     傳訊息至Line Notify
    #     """
    #     url = "https://maker.ifttt.com/trigger/ServerInformation/with/key/bmsGx8rqE3pk6bRBGhRO_k"
    #     requests.post(url, data={'value1':str(msg), 'value2':str(msg2),'value3':str(msg3)})

    @staticmethod
    def sendMessage(msg, img=None, last=False, TokenKey="TOKEN1"):
        """Send a LINE Notify message (with or without an image)."""
        parser = configparser.ConfigParser()
        parser.sections()
        parser.read(os.path.join(parent, 'Config', 'LineNotify.conf'))
        config = parser['LINENOTIFY']
        token = config[TokenKey]
        
        URL = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': 'Bearer ' + token}
        payload = {'message': msg}
        if last:
            payload.update({'stickerPackageId':8525,
                        'stickerId':16581294})
        files = {'imageFile': open(img, 'rb')} if img else None
        
        r = requests.post(URL, headers=headers, params=payload, files=files)
        if files:
            files['imageFile'].close()
        return r.status_code