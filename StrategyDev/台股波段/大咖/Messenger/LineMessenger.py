# -*- encoding: UTF-8 -*-
# Line Messenger
# CopyRight : Seth Technologies Inc. 塞特科技
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.17
# Update: Change token, update code
# Version: 1

__updated__ = '2021-09-29 15:56:30'
import requests
from datetime import datetime

class LineMessenger:

    token = "YQPO9SzkHgmUoVtQRvKXwdKuzSKwGSSrb9OaI73w8Uy"
    @staticmethod
    def sendPhoto(msg, picURI, last=False, token=None):
        return LineMessenger.sendMessage(msg, last, picURI, token)

    @staticmethod
    def sendMessage(msg, last=False, img=None, token=None):
        """
        傳訊息至Line Notify
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        """Send a LINE Notify message (with or without an image)."""
        
        URL = 'https://notify-api.line.me/api/notify'
        if not token: token = LineMessenger.token
        headers = {'Authorization': 'Bearer ' + token}
        payload = {'message': f'\n【{now}】\n\n{msg}'}
        if last:
            payload.update({'stickerPackageId':8525,
                        'stickerId':16581297})
        files = {'imageFile': open(img, 'rb')} if img else img
        
        r = requests.post(URL, headers=headers, params=payload, files=files)
        if files:
            files['imageFile'].close()
        return r.status_code

    @staticmethod
    def sendDocument(msg, filepath, token=None):
        url = "https://notify-api.line.me/api/notify"
        if not token: token = LineMessenger.token
        headers = {"Authorization":"Bearer " + token}
        payload = {'message': msg}
        files = {'Document': open(filepath, 'rb')}
        r = requests.post(url, headers = headers, params = payload, files = files)