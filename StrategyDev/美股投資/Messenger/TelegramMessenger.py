# -*- encoding: UTF-8 -*-
# Telegram Messenger
# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.17
# Version: 1

__updated__ = '2020-11-25 23:27:20'

import requests
from telegram import Bot
import os
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path):
    path = os.getcwd()
    
group_map = {
    'CapitalFlows':'-437393670',
    'Money':'-456934820'
    }

class TelegramMessenger:

    @staticmethod
    def bot(token="957393505:AAGzPt9UoTq-f1mhtOiFVQKODkiooH7HWWU"):
        return Bot(token)
        
    @staticmethod
    def sendPhoto(text, picURI, token="957393505:AAGzPt9UoTq-f1mhtOiFVQKODkiooH7HWWU", group='Money'):
        # chatId = "-456547419" #(此處的chatID請參考Reference從網頁版登入後可以取得)
        chatId = group_map[group]
        TelegramMessenger.bot(token).sendPhoto(chat_id=chatId, photo=open(picURI, 'rb'), caption=text)

    @staticmethod
    def sendMessage(text, token="957393505:AAGzPt9UoTq-f1mhtOiFVQKODkiooH7HWWU", group='Money'):
        """
        傳訊息至Telegram Group
        """
        # chatId = "-456547419" #(此處的chatID請參考Reference從網頁版登入後可以取得)
        chatId = group_map[group]
        TelegramMessenger.bot(token).sendMessage(chat_id=chatId, text=text)

if __name__ == "__main__":
    TelegramMessenger.sendMessage('hello')
    # TelegramMessenger.sendPhoto('hello photo', os.path.join(path, '希奇資本 LOGO.png'))
