import pandas as pd
import matplotlib.pyplot as plt
import os
from modules import Mongo

__updated__ = '2020-11-21 16:43:40'

###   WeeklyReturn of Stocks   ###
def WeeklyReturn(Ticker, end, Data_Actions, Data_Close):

   if len(Data_Close) > 0:
      Data_All = pd.DataFrame(index = [d for d in pd.date_range(Data_Close.index[0], Data_Close.index[-1]).date if d in Data_Close.index], columns=['Multiplier']).fillna(1)
      j = 0 
      #for i in range(len(Data_Actions)):
      for i, idx in enumerate(Data_Actions.index):
         # idx = Data_Actions.index
         if Data_Close.index[0] < idx <= Data_Close.index[-1]:
            Data_All.loc[idx : Data_Close.index[-1], j] = 1
            try:
               values = Data_Actions.ix[i, 'Value']
            except:
               values = Data_Actions.loc[idx, 'Value']
            previous_close = Data_Close.loc[Data_All.index[0] : idx, 'Close'][-2] 
            try:
               if Data_Actions.ix[i, 'Action'] == 'XD':
                  Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1 - values / previous_close
               elif Data_Actions.ix[i, 'Action'] == 'SP':        
                  Data_All.loc[Data_All.index[0] : idx, j][:-1] = values
               elif Data_Actions.ix[i, 'Action'] == 'XR':
                  Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1000 / (1000 + values)
               elif Data_Actions.ix[i, 'Action'] == 'RC': 
                  Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1 - values / previous_close
               elif Data_Actions.ix[i, 'Action'] == 'RS':        
                  Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1000 / values 
            except:
               if isinstance(Data_Actions.loc[idx, 'Action'], str):
                  if Data_Actions.loc[idx, 'Action'] == 'XD':
                     Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1 - values / previous_close
                  elif Data_Actions.loc[idx, 'Action'] == 'SP':        
                     Data_All.loc[Data_All.index[0] : idx, j][:-1] = values
                  elif Data_Actions.loc[idx, 'Action'] == 'XR':
                     Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1000 / (1000 + values)
                  elif Data_Actions.loc[idx, 'Action'] == 'RC': 
                     Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1 - values / previous_close
                  elif Data_Actions.loc[idx, 'Action'] == 'RS':        
                     Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1000 / values
               else:
                  Data_All.loc[Data_All.index[0] : idx, j][:-1] = 1
                  for i, action in enumerate(Data_Actions.loc[idx, 'Action'].values):
                     if action == 'XD':
                           Data_All.loc[Data_All.index[0] : idx, j][:-1] *= 1 - values[i] / previous_close
                     elif action == 'SP':        
                           Data_All.loc[Data_All.index[0] : idx, j][:-1] *= values[i]
                     elif action == 'XR':
                           Data_All.loc[Data_All.index[0] : idx, j][:-1] *= 1000 / (1000 + values[i])
                     elif action == 'RC':
                           Data_All.loc[Data_All.index[0] : idx, j][:-1] *= 1 - values[i] / previous_close
                     elif action == 'RS':        
                           Data_All.loc[Data_All.index[0] : idx, j][:-1] *= 1000 / values[i]
            Data_All.loc[:,'Multiplier'] = Data_All.loc[:,'Multiplier'] * Data_All.loc[:, j]
            j = j + 1
      Data_All = pd.concat([Data_All, Data_Close], axis = 1)#, join_axes = [Data_All.index])   
      Data_All.loc[:, 'Adj Close'] = Data_All.loc[:, 'Close'] * Data_All.loc[:, 'Multiplier'] 
      Data_All = Data_All.fillna(method = 'pad')
      Finaldata = Data_All.loc[:, list(Data_Close.columns)+['Adj Close']]
      Finaldata.index = pd.to_datetime(Finaldata.index)
      return Finaldata
   
def getTable(client, exchange='TWSE', table='historicalPrice'):
   return client['admin'][exchange][table]

def getClose(client, ticker, exchange, end):
   # Data : Data_Close, Data_Actions
   Data_Close = getTable(client, exchange).find({'Date':{'$lte':end}, 'Ticker': ticker}).sort('Date') #'$gte': startdate
   Data_Close = [d for d in Data_Close]
   Data_Close = pd.DataFrame(Data_Close)
   if len(Data_Close) > 0:
      Data_Close.index = pd.to_datetime(Data_Close['Date']).apply(lambda x: x.date())
      Data_Close = Data_Close[['_id' ,'Open', 'High', 'Low', 'Close', 'Volume']]
      # Data_Close[['Open', 'High', 'Low', 'Close']] = Data_Close[['Open', 'High', 'Low', 'Close']].astype(float)
      Data_Close['Open'] = Data_Close['Open'].apply(lambda x: float(x) if x != '--' else x)
      Data_Close['High'] = Data_Close['High'].apply(lambda x: float(x) if x != '--' else x)
      Data_Close['Low'] = Data_Close['Low'].apply(lambda x: float(x) if x != '--' else x)
      Data_Close['Close'] = Data_Close['Close'].apply(lambda x: float(x) if x != '-' else x)
      Data_Close['Volume'] = Data_Close['Volume'].apply(lambda x: float(x) if x != '--' else x)
   return Data_Close

def getActions(client, ticker, exchange, end):
   Data_Actions = getTable(client, exchange, 'Actions').find({'Date':{'$lte': end}, 'Ticker': ticker}).sort('Date') # '$gte': startdate
   Data_Actions = [d for d in Data_Actions]
   Data_Actions = pd.DataFrame(Data_Actions)
   if len(Data_Actions) == 0:
      Data_Actions = pd.DataFrame(columns = ['Date', 'Ticker', 'Action', 'Value'])
   else:
      Data_Actions = Data_Actions[['Date', 'Ticker', 'Action', 'Value']]
      Data_Actions.index = pd.to_datetime(Data_Actions['Date']).apply(lambda x: x.date())
      Data_Actions = Data_Actions.drop('Date', axis = 1)
      Data_Actions['Value'] = Data_Actions['Value'].astype(float)
   return Data_Actions

def getDataWithAdjClose(client, ticker, exchange, startdate, end, Data_Actions=None, Data_Close=None):
   if Data_Close is None: Data_Close = getClose(client, ticker, exchange, end)
   if Data_Actions is None: Data_Actions = getActions(client, ticker, exchange, end)
   data = WeeklyReturn(ticker, end, Data_Actions, Data_Close)
   return data[data.index>=pd.to_datetime(startdate)]

if __name__ == '__main__':
   
   ### Mongo Database   ###
   client = Mongo()
   ticker = '1109'
   startdate = '1980-01-01'
   end = '2020-07-24'
   data = getDataWithAdjClose(client, ticker, 'TWSE', startdate, end)
   print(data)
   data['Close,Adj Close'.split(',')].plot()
   plt.show()