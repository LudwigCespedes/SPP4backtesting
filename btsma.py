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
    n1 = 2
    n2 = 124
    opt_ranges = {
        'n1': range(2, 300, 1),
        'n2': range(2, 300, 1),
    }

    def init(self):
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell( )
       
btc_data = btc_data * 10**-6

stats = walk_forward(btc_data,BTSMA)
plot_stats(stats)





# %%
stats
# %%
