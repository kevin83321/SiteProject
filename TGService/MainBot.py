# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Update: 2022.1.31
# Version: 0.0.0

from calendar import c
import random, os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ParseMode
# import pandas as pd
# import json
from TGBot.MessageReply import reply_order, set_stock, reply_more_info, backtest, updatebot, show_help_info, show_strategy_info, show_strategy_list_buttons, reply_stock_figure
# from CallbackReply import set_stock1, set_strategy, runbacktest, placeorder
# from PrepareForBot import add_user, get_user_list, read_stock_dict
#from datetime import datetime
from TGBot.Log.TransforException import GetException
from TGBot.Messenger.TelegramMessenger import TelegramMessenger as tele

def sendError(func_name):
    tele.sendMessage(f'In {str(__file__)} {func_name}, Error : {GetException()}')

def start(bot, update):
    global kb_markup
    global backtest_setting
    chat_id = update.message.chat_id
    # backtest_setting[chat_id] = backtest_setting.get(chat_id, {})
    # add_user(user_list, chat_id, path)
    text = "`使用說明` : 跳出此訊息，說明機器人之使用方法\n"
    try:
        bot.send_message(chat_id=update.message.chat_id, text="\n*歡迎訪問凱文的私人秘書* \n\n"+"==================\n"+"以下為小秘書的功能之簡介:\n\n"+text, 
                        reply_markup=kb_markup, parse_mode=ParseMode.MARKDOWN)
        # bot.send_photo(chat_id=update.message.chat_id,text='test', photo=open(os.path.join(path, '希奇資本 LOGO.jpg'), 'rb'),
        #                 caption="\n*歡迎使用希奇資本行動交易機器人* \n\n"+"==================\n"+"以下為本機器人功能之簡介:\n\n"+text, parse_mode=ParseMode.MARKDOWN,
        #                 reply_markup=kb_markup)
    except:
        sendError('start')
        bot.send_message(chat_id=update.message.chat_id, text="\n*歡迎訪問凱文的私人秘書* \n\n"+"==================\n"+"以下為小秘書的功能之簡介:\n\n"+text, 
                        reply_markup=kb_markup, parse_mode=ParseMode.MARKDOWN)

def test(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="\n*測試回覆功能* \n\n"+"==================\n"+"以下為小秘書的功能之簡介:\n\n",#+text, 
                            reply_markup=kb_markup, parse_mode=ParseMode.MARKDOWN)

def CallbackProcess(bot, update):
    # print(update.)
    data = update.callback_query.data.split(',')
    chat_id = update.callback_query.from_user.id
    # print(data)
    # backtest_setting[chat_id] = backtest_setting.get(chat_id, {})
    # setting = backtest_setting[chat_id]
    # add_user(user_list, chat_id, path)
    try:
        pass
        # if 'startsetting' in data:
        #     setting = backtest_setting[chat_id] = {}
        #     set_stock1(bot, chat_id)
        # elif 'strategy' in data:
        #     set_strategy(bot, chat_id, data, setting)
        # elif 'Run' in data:
        #     runbacktest(bot, chat_id, setting, stock_id_name)
        # elif 'placeorder' in data:
        #     placeorder(bot, chat_id)
        # elif 'Reset_Strategy' in data:
        #     del setting['strategy']
        #     show_strategy_list_buttons(bot, chat_id)
        # elif 'Reset_Stock' in data:
        #     del_list = [k for k in setting.keys() if 'stock' in k]
        #     for k in del_list:
        #         del setting[k]
        #     set_stock1(bot, chat_id)
    except:
        sendError('CallbackProcess')
        bot.send_message(chat_id=chat_id, text="發生問題,已請相關人員處理")

def message_process(bot, update, user_data):
    msg = update.message.text.lower()
    chat_id = update.message.chat_id
    # if "-" not in chat_id:
    #     chat_id = update.message.from_user.id
    # print(chat_id)
    # print(chat_id)
    print(f"{msg} in message_process")
    # backtest_setting[chat_id] = backtest_setting.get(chat_id, {})
    # setting = backtest_setting.get(chat_id, {})
    # add_user(user_list, chat_id, path)
    try:
        if '-' in msg:
            ## Do plot stock figure
            if len(msg.split('-')) == 3:
                reply_stock_figure(bot, chat_id, msg)
            # set_stock(bot, chat_id, msg.replace('.tw',''), setting, stock_id_name)
        elif '使用說明' in msg:
            show_help_info(bot, chat_id)
    except:
        sendError('message_process')
        bot.send_message(chat_id=chat_id, text="發生問題,已請相關人員處理")

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(path):
        path = os.getcwd()
    kb = [[KeyboardButton('使用說明')]]
    kb_markup = ReplyKeyboardMarkup(kb)
    # user_list = get_user_list(path)
    #stock_button_dict = create_stock_inlinebutton(stock_dict, stock_id_name)
    # Connect to your bot with token
    updater = Updater('1473321627:AAHCL7sLppLCSdxcKDMGjvaHWmoxUk2quOY')
    # set bottons and quit link
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, message_process, pass_user_data=True))
    updater.dispatcher.add_handler(CallbackQueryHandler(CallbackProcess))
    # launch backend engine
    try:
        updater.start_polling()
        updater.idle()
    except:
        os._exit(0)