from binance.client import Client
from binance.enums import *
import numpy as np
import pandas as pd
import websocket, json, pprint, csv, datetime
import talib as ta
from config import *
from Strategies import actions
import matplotlib.pyplot as plt

# Creat client object
client = Client(bnb_api_key, bnb_api_secret)

# Initialize parameters for trading
trade_symbol = 'maticusdt'
trade_quantity = 0.0004
SOCKET = f'wss://stream.binance.com:9443/ws/{trade_symbol}@kline_5m'

# get the past 1 day data to be appended with realtime data
hist_klines = client.get_historical_klines(trade_symbol.upper(), Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")

kline_columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
                'Quote Asset Volume', 'Number of Trades', 'Taker buy base asset volume',
                'Taker buy quote asset volume', 'Ignore']

kline_df = pd.DataFrame(hist_klines, columns=kline_columns)
closes = []
for i in kline_df['Close']:
    closes.append(float(i))

log_columns = ['Time','Close','MACD','RSI', 'Action', 'Status']
trade_log = pd.DataFrame(columns=log_columns)

is_position = False

# # Define order method
# def order(side, symbol, quantity, order_type = ORDER_TYPE_MARKET):
#     try:
#         order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
#     except Exception as e:
#         print("an exception occured - {}".format(e))
#         return False
#     return True

# Get realtime data with binance websocket
def on_open(ws):
    print('Opened Conection')

def on_close(ws):
    print('Close Connection')

def on_message(ws, message):
    global is_position, closes, trade_log

    json_message = json.loads(message)
    # pprint.pprint(json_message)
    candle = json_message['k']
    is_candle_close = candle['x']
    close = candle['c']

    if is_candle_close == True:
        print(f'Candle closed at {close}')
        closes.append(float(close))
        # Strategy
        macd, macdsignal, macdhist = ta.MACD(np.array(closes) , fastperiod=12, slowperiod=26, signalperiod=9)
        rsi = ta.RSI(np.array(closes), timeperiod=14)

        today_date = str(datetime.date.today())
        trade_log.to_csv(f'/Users/dragonmy/Desktop/Kit_Trader/logs/{trade_symbol}_{today_date}.csv')

        # Buy
        if macd[-1] > 0 and rsi[-1] > 55: 
            if is_position == False:
                is_position = True
                # order_succeeded = order(side= SIDE_BUY, symbol= trade_symbol, quantity=trade_quantity, order_type = ORDER_TYPE_MARKET)
                trade_log = trade_log.append(pd.Series([
                    candle['t']/1000,
                    close,
                    macd[-1],
                    rsi[-1],
                    'Buy',
                    'Succeeded' # order_succeeded
                ],index=log_columns),
                ignore_index= True)
            else:
                trade_log = trade_log.append(pd.Series([
                    candle['t']/1000,
                    close,
                    macd[-1],
                    rsi[-1],
                    'Hold',
                    'N/A'
                ],index=log_columns),
                ignore_index= True)
        elif macd[-1] <= 0 or rsi[-1] >= 70: #Sell
            if is_position:
                is_position = False
                # order_succeeded = order(side= SIDE_SELL, symbol= trade_symbol, quantity=trade_quantity, order_type = ORDER_TYPE_MARKET)
                trade_log = trade_log.append(pd.Series([
                    candle['t']/1000,
                    close,
                    macd[-1],
                    rsi[-1],
                    'Sell',
                    'Succeeded' # order_succeeded
                ],index=log_columns),
                ignore_index= True)
            else:
                trade_log = trade_log.append(pd.Series([
                    candle['t']/1000,
                    close,
                    macd[-1],
                    rsi[-1],
                    'Hold',
                    'N/A'
                ],index=log_columns),
                ignore_index= True)

# Start BNB-Trader
ws  = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close= on_close, on_message= on_message)
ws.run_forever()
