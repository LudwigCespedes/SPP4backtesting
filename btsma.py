# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
from optimize import walk_forward, plot_stats


# %%
btc= yf.Ticker("btc-USD")
btc_data = btc.history(start = dt.datetime(2015,1,1),
                       end=dt.datetime(2025,8,17), 
                       interval="1d")
btc_data

# %%
class BTSMA(Strategy):
    n1 = 11
    n2 = 22
    
    opt_ranges = {
        'n1': range(2, 200, 1),
        'n2': range(2, 200, 1)
    }

    def init(self):
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy(sl=(self.data.Close-self.data.Close*0.2))
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell(sl=(self.data.Close+self.data.Close*0.2))
       
btc_data = btc_data * 10**-6

stats = walk_forward(btc_data,BTSMA)
plot_stats(stats)
#bt = Backtest(btc_data, BTSMA, cash=10, commission=.0025)
#stats = bt.run() 
#bt.plot()
print(stats)
print(stats['Win Rate [%]'])




