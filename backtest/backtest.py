import backtrader as bt
from backtrader.dataseries import TimeFrame

class RSI_strategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, period=14)
        self.macd = bt.talib.MACD(self.data, fastperiod=12, slowperiod=26, signalperiod=9)
    
    def next(self):
        min_size = 20000
        if self.macd.macd > 0 and self.rsi > 55 and not self.position:
            self.buy(size=min_size)
        elif self.rsi <= 55 and self.macd.macd > 0:
            self.buy(size=min_size)
        elif self.macd.macd <= 0 and self.position:
            self.close()
        elif self.rsi > 70:
            self.close()

cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname='test_data.csv',
    dtformat= 2,
    compression= 5,
    timeframe= bt.TimeFrame.Minutes)
cerebro.adddata(data)
cerebro.addstrategy(RSI_strategy)
cerebro.run()
cerebro.plot()
print(cerebro.broker.getvalue())