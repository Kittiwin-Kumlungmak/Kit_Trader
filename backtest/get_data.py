from binance.client import Client
import csv
from config import *

client = Client(bnb_api_key, bnb_api_secret)

klines = client.get_historical_klines("DATAUSDT", Client.KLINE_INTERVAL_5MINUTE, "7 day ago UTC")

kline_columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
                'Quote Asset Volume', 'Number of Trades', 'Taker buy base asset volume',
                'Taker buy quote asset volume', 'Ignore']

with open('test_data.csv', 'w',  newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',',)
    csv_writer.writerow(kline_columns)
    for kline in klines:
        kline[0] /= 1000
        csv_writer.writerow(kline)



