# -*- encoding: UTF-8 -*-
# Telegram Messenger
# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.17
# Update: Change group for message
# Version: 1

__updated__ = '2021-01-31 04:32:16'

from telegram import Bot, Document
import os
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path):
    path = os.getcwd()

class TelegramMessenger:
    
    Groups = {
        'UpdateMessage' : '-483161572',
        'UpdateFiles' : '-559125108',
    }

    @staticmethod
    def bot(token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"):
        return Bot(token)
        
    @staticmethod
    def sendPhoto(text, picURI, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY", group='UpdateMessage'):
        chatId = TelegramMessenger.Groups.get(group, 'UpdateMessage') #(此處的chatID請參考Reference從網頁版登入後可以取得)
        TelegramMessenger.bot(token).sendPhoto(chat_id=chatId, photo=open(picURI, 'rb'), caption=text)

    @staticmethod
    def sendMessage(text, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY", group='UpdateMessage'):
        """
        傳訊息至Telegram Group
        """
        chatId = TelegramMessenger.Groups.get(group, 'UpdateMessage') #(此處的chatID請參考Reference從網頁版登入後可以取得) # 單純傳送訊息用
        TelegramMessenger.bot(token).sendMessage(chat_id=chatId, text=text)

    @staticmethod
    def sendDocument(text, filepath, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY", group='UpdateMessage'):
        chatId = TelegramMessenger.Groups.get(group, 'UpdateMessage') #(此處的chatID請參考Reference從網頁版登入後可以取得)
        TelegramMessenger.bot(token).sendDocument(chat_id=chatId, document=open(filepath,'rb'), filename=filepath.replace(os.path.dirname(filepath),'')[1:])

if __name__ == "__main__":
    TelegramMessenger.sendMessage('hello')
    TelegramMessenger.sendPhoto('hello photo', os.path.join(path, '希奇資本 LOGO.png'))
    #TelegramMessenger.sendPhoto('hello photo', os.path.join(path, '希奇資本 LOGO.png'))
