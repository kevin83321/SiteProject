# CopyRight : XIQICapital 希奇資本
# 記錄檔模組
# Author: Kevin Cheng 鄭圳宏
# Create: 2019.07.27
# Update: 2020.02.26
# Version: Test

from .TransforException import GetException
import os
from datetime import datetime
import requests


class Logger:

    def __init__(self):
        """
        Initialises datetime and log path for logging.
        :param dt:
        """
        self.dt = datetime.now()
        self._initial_log_path()

    def _initial_log_path(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.logdir = os.path.join(path, '_logs', str(self.dt.year).zfill(
            4), str(self.dt.month).zfill(2), str(self.dt.day).zfill(2))
        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)

    def _write_log(self, filename, msg):
        with open(os.path.join(self.logdir, filename+'.txt'), 'a', encoding='utf_8_sig') as f:
            t = datetime.now()
            line = f'[{str(t)}], {filename} Message : {msg}\n'
            f.write(line)

    def _write_ts_log(self, filename, head, msg):
        if not os.path.isfile(os.path.join(self.logdir, filename+'_ts.txt')):
            with open(os.path.join(self.logdir, filename+'_ts.txt'), 'w', encoding='utf_8_sig') as f:
                f.write('time,' + head)
        with open(os.path.join(self.logdir, filename+'_ts.txt'), 'a', encoding='utf_8_sig') as f:
            t = datetime.now()
            line = f'{str(t)},{msg}\n'
            f.write(line)

    def critical(self, msg):
        self._write_log('CRITICAL', msg)

    def error(self, msg):
        self._write_log('ERROR', msg)

    def debug(self, msg):
        self._write_log('DEBUG', msg)

    def warn(self, msg):
        self._write_log('WARN', msg)

    def info(self, msg):
        self._write_log('INFO', msg)