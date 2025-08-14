# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
from optimize import walk_forward

# %%
btc= yf.Ticker("btc-USD")
btc_data = btc.history(start = dt.datetime(2020,1,1),
                       end=dt.datetime.now(), 
                       interval="1d")
btc_data

# %%
class BTSMA(Strategy):
    n1 = 2
    n2 = 124

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
""" 
bt = Backtest(btc_data, BTSMA, cash=10, commission=.01)
#stats =bt.optimize(n1=range(2, 10,1), n2=range(2, 10,1), 
#                   maximize= lambda x: x['Return [%]']
#                                        /x['Buy & Hold Return [%]'],
#                                        constraint=lambda p: p.n1 < p.n2)
stats = bt.run()
print(stats)
bt.plot()
"""

# %%
lookback_bars = 28*1440
validation_bars = 16*68

stats = walk_forward(BTSMA,btc_data,100,100,100)



# %%
stats
# %%
