from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy, MultiBacktest
#from backtesting.test import MultiBacktest
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
from optimize import walk_forward, plot_stats
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
class BTMACD(Strategy):
    n1=42
    n2=82
    signal=2
    adx_time = 82
    adx_pass = 2
    
    opt_ranges =  {"n1": range(2,100,1),
                   "n2": range(2,100,1),
                   "signal": range(2,100,1),
                   "adx_time" : range(2,100,1),
                   "adx_pass":range(2,100,1)}
    
    def init(self):
        self.macd, self.signal_line, _ = self.I(talib.MACD, self.data.Close, 
                                                fastperiod=self.n1, 
                                                slowperiod=self.n2, 
                                                signalperiod=self.signal)
        self.adx = self.I(talib.ADX,self.data.High,self.data.Low,self.data.Close,self.adx_time)

    def next(self):
        if self.adx> self.adx_pass:
            if crossover(self.macd, self.signal_line):
                preice = self.data.Close[-1]
                self.position.close()
                self.buy(size=1, sl=preice-preice * 0.2)
            elif crossover(self.signal_line, self.macd):
                self.position.close()
                preice = self.data.Close[-1]
                self.sell(size=1, sl=preice+ preice * 0.2)
                
        else:
            self.position.close() 
# %%
if __name__=="__main__":
    """
    btc = yf.Ticker('BTC-USD')
    #btc = btc.history(period = "15y",interval= "1d" ).iloc[:, :5]*10**-6
    #btc = btc.history(start=dt.datetime(2025,9,10)-dt.timedelta(days=), end =dt.datetime(2025,9,10),interval= "1d" ).iloc[:, :]*10**-6
        
    bt = Backtest((btc*10**-6),BTMACD,cash=10, commission=.01)
    stat=bt.run()
    print(stat)
    bt.plot()
    stats =walk_forward((btc*10**-6),BTMACD,
                        maximize='Alpha [%]',
                        constraint=lambda p: p.n1 < p.n2 and p.signal  < p.n1)
    plot_stats(stats)
    
    """
    btm = MultiBacktest([btc,eth,bnb,dot,cake,xau,coin,nvda,aapl],BTMACD,cash=10, commission=.01)
    stat=btm.run()
    print(stat)
    
    
