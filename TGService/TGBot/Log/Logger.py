# CopyRight : Kevin Cheng 鄭圳宏
# Author: Kevin Cheng 鄭圳宏
# Created: 2022.2.1
# Version: 0.0.0

__update__ = ""

# from xqctrader.Singleton.Singleton import Singleton
# from xqctrader.Events.ErrorEvent import ErrorEvent
from .TransforException import GetException
from TGBot.Messenger.LineMessenger import LineMessenger as Line
from TGBot.Messenger.TelegramMessenger import TelegramMessenger as Telegram
import os
from datetime import datetime
import requests

class Logger:#(Singleton):

    def __init__(self, dt, eventmanager, live_or_Backtest='RealTime'):
        """
        Initialises datetime and log path for logging.
        :param dt:
        """
        self.dt = dt
        self._eventmanger = eventmanager
        self.live_or_Backtest = live_or_Backtest
        self._initial_log_path()

    def sendError(self, func_name):
        e = GetException()
        self._eventmanger.put(ErrorEvent(f'In {str(self)}.{func_name}, Error : {e}'))

    def _initial_log_path(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.logdir = os.path.join(path, '_logs', self.dt, self.live_or_Backtest)
        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)

    def _write_log(self, filename, msg):
        with open(os.path.join(self.logdir, filename+'.txt'),'a', encoding='utf_8_sig') as f:
            t = datetime.now()
            line = f'[{str(t)}], {filename} Message : {msg}\n'
            f.write(line)
            if 'Order' in filename:
                self._sendNotify(self.dt+'_'+filename,line)

    def _write_ts_log(self, filename, head, msg):
        if not os.path.isfile(os.path.join(self.logdir, filename+'_ts.txt')):
            with open(os.path.join(self.logdir, filename+'_ts.txt'),'w', encoding='utf_8_sig') as f:
                f.write('time,' + head)
        with open(os.path.join(self.logdir, filename+'_ts.txt'),'a', encoding='utf_8_sig') as f:
            t = datetime.now()
            line = f'{str(t)},{msg}\n'
            f.write(line)
            if 'Order' in filename:
                self._sendNotify(self.dt+'_'+filename,line)

    def critical(self, event):
        self._write_log('CRITICAL', event.msg)

    def error(self, event):
        self._write_log('ERROR', event.msg)

    def debug(self, event):
        self._write_log('DEBUG', event.msg)

    def warn(self, event):
        self._write_log('WARN', event.msg)

    def info(self, event):
        self._write_log('INFO', event.msg)

    def order_failed(self, event):
        try:
            text = []
            for k, v in event.data.items():
                head.append(str(k))
                text.append(f'{k}:{v}')
            msg = ', '.join(text)
            self._write_log('OrderFailed', msg)
        except:
            try:
                msg = event.data
                self._write_log('OrderFailed', msg)
            except:
                self.sendError('order_msg')        

    def order_msg(self, event):
        try:
            head = []
            text = []
            for k, v in event.data.items():
                head.append(str(k))
                text.append(str(v))
            head = ','.join(head)
            msg = ','.join(text)
            self._write_ts_log('OrderMsg', head, msg)
        except:
            try:
                msg = event.data
                self._write_log('OrderMsg', msg)
            except:
                self.sendError('order_msg')

    def signal_msg(self, event):
        try:
            head = []
            text = []
            for k, v in event.__dict__.items():
                head.append(str(k))
                text.append(str(v))
            head = ','.join(head)
            msg = ','.join(text)
            self._write_ts_log('SignalMsg', head, msg)
        except:
            self.sendError('signal_msg')

    def fill_msg(self, event):
        try:
            head = []
            text = []
            for k, v in event.__dict__.items():
                head.append(str(k))
                text.append(str(v))
            head = ','.join(head)
            msg = ','.join(text)
            self._write_ts_log('FillMsg', head, msg)
        except:
            self.sendError('fill_msg')

    def holding_msg(self, event):
        try:
            head = []
            text = []
            for k, v in event.__dict__.items():
                head.append(str(k))
                text.append(str(v))
            head = ','.join(head)
            msg = ','.join(text)
            self._write_ts_log('Holding_Msg', head, msg)
        except:
            self.sendError('holding_msg')

    def account_msg(self, event):
        pass

    def _sendNotify(self, msg='', msg2='', msg3='This is from Logger'):
        Line.sendMessage(msg, msg2, msg3)
        Telegram.sendMessage("\n".join([msg, msg2, msg3]))