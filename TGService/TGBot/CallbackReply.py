# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Update: 2019.11.08
# Version: 0.0.0

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from PlotGraph import PlotSingleAsset
from MessageReply import show_run_backtest
from StrategyFunction import *
from Log.TransforException import GetException
from Messenger.TelegramMessenger import TelegramMessenger as tele

def sendError(func_name):
    tele.sendMessage(f'In {str(__file__)}.{func_name}, Error : {GetException()}')

def placeorder(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,
                            text='需經金管會同意')
    except:
        sendError('placeorder')

def set_stock1(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,text="請輸入第一個股票代號加上 *.tw* 或是 *.TW*，\n例如:2330.tw 或是 2330.TW", parse_mode=ParseMode.MARKDOWN)
    except:
        sendError('set_stock1')

def set_stock2(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,
                            text="請輸入第二個股票代號加上 *.tw* 或是 *.TW*，\n例如:3008.tw 或是 3008.TW", parse_mode=ParseMode.MARKDOWN
                            )
    except:
        sendError('set_stock2')

def set_strategy(bot, chat_id, data, setting):
    strategy = data[1]
    try:
        if strategy == 'PairsTrading':
            setting['strategy'] = [strategy, PairsTrading]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            elif 'stock2' not in setting.keys():
                set_stock2(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'TrendFollowing':
            setting['strategy'] = [strategy, TrendFollowing]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'MeanReversion':
            setting['strategy'] = [strategy, MeanReversion]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'BBand':
            setting['strategy'] = [strategy, BBand]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'RSI':
            setting['strategy'] = [strategy, RSI]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'MACD':
            setting['strategy'] = [strategy, MACD]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'MAC':
            setting['strategy'] = [strategy, MAC]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'ICHIMOKU':
            setting['strategy'] = [strategy, ICHIMOKU]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
        elif strategy == 'CUSUM':
            setting['strategy'] = [strategy, CUSUM]
            if 'stock1' not in setting.keys():
                set_stock1(bot, chat_id)
            else:
                show_run_backtest(bot, chat_id)
    except:
        sendError('set_strategy')

def runbacktest(bot, chat_id, setting, stock_id_name):
    try:
        strategy = setting['strategy'][1]
        strategy(bot, chat_id, setting, stock_id_name)
    except:
        sendError('runbacktest')