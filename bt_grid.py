# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import backtesting
from optimize import walk_forward, plot_stats
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
import datetime as dt
import talib
import numpy as np


# %%
btc_data = yf.Ticker('BTC-USD')
#btc = btc_data.history(start=dt.datetime(2025,8,12)-dt.timedelta(days=728), end =dt.datetime(2025,8,11),interval= "4h" ).iloc[:, :4]*10**-6
#btc 
btc_data = btc_data.history(start = dt.datetime(2015,1,1),
                       end=dt.datetime(2025,8,17), 
                       interval="1d").iloc[:, :4]
btc_data
# %%
def grid(data,grid_buy):
    return data-(data*grid_buy)
class GridInfinity(Strategy):
    grid_n = 20
    grid_profy =1
    grid_buy = 1
    opt_ranges = {
        'grid_n': range(2, 100, 1),
        'grid_profy': range(2, 100, 1),
        'grid_buy': range(2,100,1)
    }
    def init(self):
        #self.buy_order =self.I(grid,self.data.Close,grid_buy = self.grid_buy )
        #self.buy_order = resample_apply('7d',grid,self.data.Close,grid_buy = self.grid_buy)
        pass
    def next(self):
        price=self.data.Close
        self.buy(limit=price-(price * (self.grid_buy/100)),size=1, tp=price+(price * (self.grid_profy/100)) )

        #if crossover(self.data.Close, self.buy_order):
        #    preice = self.data.Close
        #    self.buy(size=1, tp=preice+(preice * self.grid_profy))
 
# %%
"""
bt = Backtest(btc ,GridInfinity , cash=10, commission=.01)
stats = bt.optimize(grid_profy =range(1,10),
    grid_buy = range(1,10), 
    maximize='Alpha [%]')
#stats = bt.run()
bt.plot()
print(stats)
print(stats._strategy)
"""
btc_data = btc_data * 10**-6

#stats = walk_forward(btc_data,BTSMA)
#plot_stats(stats)
bt = Backtest(btc_data, GridInfinity, cash=10, commission=.0025)
#stats = bt.run() 
#bt.plot()
stats = walk_forward(btc_data,GridInfinity)
plot_stats(stats)
print(stats)
print(stats['Win Rate [%]'])
