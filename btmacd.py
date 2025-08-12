from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
# %%
btc = yf.Ticker("BTC-USD")
btc_data = btc.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 1, 1),
                        interval="1d")
btc_data = btc_data * 10**-6  # Normalize the data
# %%
class BTMACD(Strategy):
    n1 = 12
    n2 = 26
    signal = 9

    def init(self):
        self.macd, self.signal_line, _ = self.I(talib.MACD, self.data.Close, 
                                                fastperiod=self.n1, 
                                                slowperiod=self.n2, 
                                                signalperiod=self.signal)

    def next(self):
        if crossover(self.macd, self.signal_line):
            preice = self.data.Close[-1]
            self.position.close()
            self.buy(size=1, sl=preice-preice * 0.1)
        elif crossover(self.signal_line, self.macd):
            self.position.close()
            preice = self.data.Close[-1]
            self.sell(size=1, sl=preice+ preice * 0.1)
# %%
bt = Backtest(btc_data, BTMACD, cash=10, commission=.01)
stats = bt.optimize(n1=range(2, 30, 5), n2=range(2, 30, 5),
                   signal=range(2, 30, 5), maximize='Alpha [%]')