# -*- encoding: UTF-8 -*-
# Telegram Messenger
# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Create: 2020.02.17
# Update: 2024.06.12
# Version: 1

__updated__ = '2024-06-12 02:35:54'

from telegram import Bot, ParseMode

class TelegramMessenger:

    @staticmethod
    def bot(token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY") -> Bot:
        return Bot(token)
        
    @staticmethod
    def sendPhoto(text, picURI, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"):
        chatId = "-420424644" #(此處的chatID請參考Reference從網頁版登入後可以取得)
        try:
            TelegramMessenger.bot(token).send_photo(chat_id=chatId, photo=open(picURI, 'rb'), caption=text, parse_mode=ParseMode.MARKDOWN_V2)
        except:
            from utils import GetException
            print(GetException())
            TelegramMessenger.bot(token).send_photo(chat_id=chatId, photo=open(picURI, 'rb'), caption=text)

    @staticmethod
    def sendMessage(text, token="1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY"):
        """
        傳訊息至Telegram Group
        """
        chatId = "-420424644"  #(此處的chatID請參考Reference從網頁版登入後可以取得)
        try:
            TelegramMessenger.bot(token).send_message(chat_id=chatId, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        except:
            from utils import GetException
            print(GetException())
            TelegramMessenger.bot(token).send_message(chat_id=chatId, text=text)

if __name__ == "__main__":
    TelegramMessenger.sendMessage('hello')
    # TelegramMessenger.sendPhoto('hello photo', os.path.join(path, '希奇資本 LOGO.png'))
