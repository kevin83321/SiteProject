# -*- encoding: UTF-8 -*-
# Telegram Messenger
# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.17
# Update: 2020.02.17
# Version: 1

from telegram import Bot

class TelegramMessenger:

    @staticmethod
    def bot(token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"):
        return Bot(token)
        
    @staticmethod
    def sendPhoto(text, picURI, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"):
        chatId = "-420424644" #(此處的chatID請參考Reference從網頁版登入後可以取得)
        TelegramMessenger.bot(token).sendPhoto(chat_id=chatId, photo=open(picURI, 'rb'), caption=text)

    @staticmethod
    def sendMessage(text, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"):
        """
        傳訊息至Telegram Group
        """
        chatId = "-420424644"  #(此處的chatID請參考Reference從網頁版登入後可以取得)
        TelegramMessenger.bot(token).sendMessage(chat_id=chatId, text=text)

if __name__ == "__main__":
    TelegramMessenger.sendMessage('hello')
    # TelegramMessenger.sendPhoto('hello photo', os.path.join(path, '希奇資本 LOGO.png'))
