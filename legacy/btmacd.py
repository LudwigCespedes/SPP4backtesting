from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
from optimize import walk_forward, plot_stats
# %%
btc = yf.Ticker("BTC-USD")
btc_data = btc.history(start=dt.datetime(2015, 1, 1),
                        end=dt.datetime(2025, 1, 1),
                        interval="1d")
btc = btc_data
# %%
class BTMACD(Strategy):
    """
    n1 = 12
    n2 = 26
    signal = 9
    """
    n1=42
    n2=82
    signal=2
    opt_ranges =  {"n1": range(2,100,10),
                   "n2": range(2,100,10),
                   "signal": range(2,100,10)}
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
if __name__=="__main__":
    bt = Backtest((btc*10**-6),BTMACD,cash=10, commission=.01)
    
    stat=bt.run()
    print(stat)
    bt.plot()
    
    stats =walk_forward((btc*10**-6),BTMACD,
                        maximize='Alpha [%]',
                        constraint=lambda p: p.n1 < p.n2 and p.signal  < p.n1)
    plot_stats(stats)