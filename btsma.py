# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
from optimize import walk_forward, plot_stats
from backtesting.lib import crossover, TrailingStrategy, MultiBacktest
import pandas as pd
import time
import multiprocessing

# %%
btc= yf.Ticker("btc-USD")
btc_data = btc.history(start = dt.datetime(2015,1,1),
                       end=dt.datetime(2025,8,17), 
                       interval="1d")
btc_data
# %%
BTC = yf.Ticker("BTC-USD")
btc = BTC.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
ETH = yf.Ticker("ETH-USD")
eth = ETH.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                 interval="1d").iloc[:, :]*10**-6
BNB = yf.Ticker("BNB-USD")
bnb = BNB.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
DOT = yf.Ticker("DOT-USD")
dot = DOT.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
CAKE = yf.Ticker("CAKE-USD")
cake = CAKE.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
XAUUSD = yf.Ticker("XAUT-USD")
xau= XAUUSD.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
COIN = yf.Ticker("COIN")
coin = COIN.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
NVDA = yf.Ticker("NVDA")
nvda = NVDA.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6
AAPL = yf.Ticker("AAPL")
aapl = AAPL.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 9, 1),
                        interval="1d").iloc[:, :]*10**-6


# %%
class BTSMA(Strategy):
    n1 = 171
    n2 = 155
    stop = 7
    #
    opt_ranges = {
        'n1': range(2, 200, 1),
        'n2': range(2, 200, 1),
        'stop': range(2, 100, 1)}

    def init(self):
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy(sl=(self.data.Close-self.data.Close*(self.stop/100)))
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell(sl=(self.data.Close+self.data.Close*(self.stop/100)))
       
if __name__=="__main__":
    
    #btc = yf.Ticker('BTC-USD')
    #btc = btc.history(period = "15y",interval= "1d" ).iloc[:, :5]*10**-6
    #btc = btc.history(start=dt.datetime(2025,9,10)-dt.timedelta(days=729), end =dt.datetime(2025,9,10),interval= "4h" ).iloc[:, :]*10**-6
    backtesting.Pool = multiprocessing.Pool
    stats =walk_forward((btc*10**-6),BTSMA,
                        maximize='Sortino Ratio',
                        constraint=lambda p: p.n1 <p.n2)
    plot_stats(stats)
    """
    
    bt = Backtest(btc,BTSMA,cash=10,commission=0.01)
    stat=bt.run()
    bt.plot()
    print(stat)
    btm = MultiBacktest([btc,eth,bnb,dot,cake,xau,coin,nvda,aapl],BTSMA,cash=10, commission=.01)
    stats=btm.run()
    print(stats)
    stats_df= pd.DataFrame(stats)
    stats_df.to_csv(f'data/{time.time()}.csv')
    """
    



