# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import backtesting
from optimize import walk_forward, plot_stats
import multiprocessing
import yfinance as yf
import datetime as dt
import talib
from backtesting.lib import crossover, TrailingStrategy, MultiBacktest

# %%
btc_data = yf.Ticker('btc-usd')
#btc = btc_data.history(start=dt.datetime(2025,7,1), end =dt.datetime(2025,8,17),interval= "5m" ).iloc[:, :4]*10**-6
btc_d1 = btc_data.history(period = "max",interval= "1d" ).iloc[:, :4]#*10**-6

# %%
class MacdAdxEmaStrategy(Strategy):
    macdfast = 12
    macdslow = 26
    macdsignal = 9
    adxperiod = 14
    emafast = 9
    emalow =50
    adxpass = 20
    opt_ranges =  {
        "macdfast" : range(10, 13),       # 8 valores
        "macdslow" : range(20, 26),      # 13 valores
        "macdsignal" : range(11, 13),     # 8 valores
        "adxperiod" : range(5, 21,2),      # 16 valores
        "emafast" : range(10, 100, 10),    # 8 valores
        "emalow" : range(10, 200, 10),   # 15 valores
        "adxpass" : range(10, 90, 10)    # 10 valores
        }
    def init(self):
        self.macd = self.I(talib.MACD, self.data.Close, 
                           fastperiod=self.macdfast, slowperiod=self.macdslow, signalperiod=self.macdsignal)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adxperiod)
        self.ema1period30mf = resample_apply('7d', talib.EMA,self.data.Close.s,self.emafast)
        self.ema2period30ml = resample_apply('7d', talib.EMA, self.data.Close,self.emalow)  

    def next(self):
        if(self.adx > self.adxpass) and (self.ema1period30mf > self.ema2period30ml):
                if self.position.is_short:
                    self.position.close()
                if crossover(self.macd[0], self.macd[1]):
                    self.buy()
                elif crossover(self.macd[1], self.macd[0]):
                    self.position.close()

        elif (self.adx > self.adxpass) and (self.ema1period30mf < self.ema2period30ml):
                if self.position.is_long:
                    self.position.close()                
                if crossover(self.macd[1], self.macd[0]):
                    self.sell()
                elif crossover(self.macd[0], self.macd[1]):
                    self.position.close()

        elif self.adx < self.adxpass:
            self.position.close()


# %%
if __name__=="__main__":
    backtesting.Pool = multiprocessing.Pool
    stats =walk_forward((btc_d1*10**-6),MacdAdxEmaStrategy,
                        maximize='Alpha [%]',
                        constraint=lambda p: p.macdfast < p.macdslow and p.emafast < p.emalow and p.adxperiod < p.adxpass)
    plot_stats(stats)


