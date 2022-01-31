# CopyRight : XIQICapital 希奇資本
# Author: Kevin Cheng 鄭圳宏
# Update: 2019.11.08
# Version: 0.0.0

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ParseMode
# from PlotGraph import PlotSingleAsset, PlotSingleAssetInterDay

from Log.TransforException import GetException
from Messenger.TelegramMessenger import TelegramMessenger as tele

def sendError(func_name):
    tele.sendMessage(f'In {str(__file__)} {func_name}, Error : {GetException()}')

def send_history_plot(bot, chat_id, data, stock_id_name):
    try:
        s_name = stock_id_name.get(data, "")
        figfile = PlotSingleAsset(data)
        bot.send_photo(chat_id=chat_id,photo=open(figfile,'rb'), caption=f'\n上圖是 {s_name}({data}) 的歷史價格走勢')
    except:
        sendError('send_history_plot')
        raise

def send_history_plot_interday(bot, chat_id, data, stock_id_name):
    try:
        s_name = stock_id_name.get(data, "")
        figfile = PlotSingleAssetInterDay(data)
        bot.send_photo(chat_id=chat_id,photo=open(figfile,'rb'), caption=f'\n上圖是 {s_name}({data}) 的歷史價格走勢')
    except:
        sendError('send_history_plot_interday')
        raise

def set_stock(bot, chat_id, data, setting, stock_id_name):
    try:
        if 'stock1' not in setting.keys():
            try:
                send_history_plot_interday(bot, chat_id, data, stock_id_name)
                #send_history_plot(bot, chat_id, data, stock_id_name)
            except:
                sendError(f'set_stock for stock1 : {data}')
                reply_no_data(bot,chat_id,data)
            else:
                setting['stock1'] = data
                if 'strategy' not in setting.keys():
                    show_strategy_list_buttons(bot, chat_id)
                else:
                    show_run_backtest(bot, chat_id)
        elif 'stock2' not in setting.keys():
            try:
                send_history_plot_interday(bot, chat_id, data, stock_id_name)
                #send_history_plot(bot, chat_id, data, stock_id_name)
            except:
                sendError(f'set_stock for stock2 : {data}')
                reply_no_data(bot,chat_id,data)
            else:
                setting['stock2'] = data
                if 'strategy' not in setting.keys():
                    show_strategy_list_buttons(bot, chat_id)
                else:
                    show_run_backtest(bot, chat_id)
        elif 'strategy' not in setting.keys():
            show_strategy_list_buttons(bot, chat_id)
        else:
            show_run_backtest(bot, chat_id)
    except:
        sendError('set_stock')
        raise

def reply_no_data(bot, chat_id, data):
    try:
        bot.send_message(chat_id=chat_id,
                        text=f'{data} 這支股票不存在或近期無交易紀錄')
    except:
        sendError('reply_no_data')

def show_strategy_list_buttons(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,
                        text='請選擇您要使用的策略',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton('MACD', callback_data='strategy,MACD'),
                            InlineKeyboardButton('布林通道(BBand)', callback_data='strategy,BBand')],
                            [InlineKeyboardButton('強弱指標(RSI)', callback_data='strategy,RSI'),
                            InlineKeyboardButton('均線交叉(MACross)', callback_data='strategy,MAC')],
                            [InlineKeyboardButton('ICHIMOKU', callback_data='strategy,ICHIMOKU'),
                            InlineKeyboardButton('CUSUM', callback_data='strategy,CUSUM')],
                            [InlineKeyboardButton('配對交易(PairsTrading)', callback_data='strategy,PairsTrading')
                            #,InlineKeyboardButton('趨勢策略', callback_data='Strategy,TrendFollowing')
                            #,InlineKeyboardButton('震盪策略', callback_data='Strategy,MeanReversion')
                        ]]))
    except:
        sendError('show_strategy_list_buttons')

def show_run_backtest(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id
                        ,text='設定已完成，請按開始回測,或選擇看更多。'
                        ,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('開始回測',callback_data='Run'), InlineKeyboardButton('更多', url='xiqicapital.com')],
                                                            [InlineKeyboardButton('換標的',callback_data='Reset_Stock'), InlineKeyboardButton('換策略',callback_data='Reset_Strategy')]
                                                            ]))
    except:
        sendError('show_run_backtest')

def backtest(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,
                        text="歡迎使用回測功能",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton('開始選股', callback_data='startsetting'),
                            InlineKeyboardButton('看更多', url='xiqicapital.com')
                        ]]))
    except:
        sendError('backtest')
        raise

def updatebot(bot, chat_id, kb_markup):
    try:
        bot.send_message(chat_id=chat_id,
                                text="已經更新到最新了",
                                reply_markup=kb_markup)
    except:
        sendError('updatebot')

def show_help_info(bot, chat_id):
    try:
        text = "`使用說明` : 跳出此訊息，說明機器人之使用方法\n"
        bot.send_message(chat_id=chat_id,text=text, parse_mode=ParseMode.MARKDOWN)
    except:
        sendError('show_help_info')

def show_strategy_info(bot, chat_id):
    try:
        text="""
        *策略說明 : *\n\
    `配對交易` : 源自於華爾街Morgan Stanley統計套利策略，由投資人選擇2支股票，利用演算法將過去1個月高估的股票放空，低估的股票做多，並等待價差收斂套利。有別於傳統的老師報明牌以及號稱用人工智慧預測股票走勢。
        """
        bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    except:
        sendError('show_strategy_info')

def reply_order(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,
                            text='需經金管會同意')
    except:
        sendError('reply_order')

def reply_more_info(bot, chat_id):
    try:
        bot.send_message(chat_id=chat_id,
                                text='請點以下連結',#'<a href="mailto:xiqicpt@gmail.com">聯絡我們</a>',
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='聯絡我們',url = 'xiqicapital.com')]])
                                )
    except:
        sendError('reply_more_info')