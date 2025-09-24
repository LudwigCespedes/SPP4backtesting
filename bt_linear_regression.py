from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import backtesting
from optimize import walk_forward, plot_stats
import yfinance as yf
import datetime as dt
import talib
class MacdRsiAd(Strategy):
    macd_n1 = 46
    macd_n2 = 25
    macd_signal = 44
    rsi_p = 14
    l =20
    l_raw = 50
    h = 70
    h_raw = 50
    opt_ranges =  {"macd_n1": range(2,50),
                   "macd_n2": range(2,50),
                   "macd_signal": range(2,50)}
    def init(self):
        self.ad_line = self.I(talib.AD,self.data.High, self.data.Low, self.data.Close, self.data.Volume)
        self.rsi = self.I(talib.RSI,self.ad_line,self.rsi_p)
        self.macd =self.I(talib.MACD,self.ad_line,self.macd_n1,self.macd_n2,self.macd_signal)
        
    def next(self):
        if self.rsi>self.l_raw and crossover(self.macd[0],self.macd[1]) :
        #if crossover(self.macd[0],self.macd[1]) :
            self.position.close()
            self.buy()
        #elif crossover(self.macd[1],self.macd[0]):
        if self.rsi<self.h_raw and crossover(self.macd[1],self.macd[0]) :
            self.position.close()
            self.sell()

        
         

if __name__=="__main__":
    btc = yf.Ticker('BTC-USD')
    #btc = btc.history(period = "15y",interval= "1d" ).iloc[:, :5]*10**-6
    btc = btc.history(start=dt.datetime(2025,9,10)-dt.timedelta(days=729), end =dt.datetime(2025,9,10),interval= "4h" ).iloc[:, :]*10**-6
    """
    stats =walk_forward((btc*10**-6),MacdRsiAd,
                        maximize='Alpha [%]',
                        constraint=lambda p: p.macd_n1 >p.macd_signal)
    plot_stats(stats)
    """
    
    bt = Backtest(btc,MacdRsiAd,cash=100,commission=0.01)
    stats=bt.run()
    bt.plot()
    print(stats)
    