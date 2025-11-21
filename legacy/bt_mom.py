from backtesting import Backtest, Strategy
from backtesting.lib import crossover, resample_apply
import backtesting
from optimize import walk_forward, plot_stats
import yfinance as yf
import datetime as dt
import talib
class RocAD(Strategy):
    roc_p=10
    roc_lr =12
    roc_hr = 14
    
    
    opt_ranges =  {"roc_p": range(2,100),
                   "roc_lr": range(2,100),
                   "roc_hr": range(2,100)}
    def init(self):
        self.ad_line = self.I(talib.AD,self.data.High, self.data.Low, self.data.Close, self.data.Volume)
        self.roc =self.I(talib.ROC,self.ad_line,self.roc_p)
        
    def next(self):
        if self.roc>self.roc_hr :
            self.position.close()
            self.buy()
        elif self.roc<-self.roc_lr :
            self.position.close()
            self.sell()
            
if __name__=="__main__":
    btc = yf.Ticker('BTC-USD')
    #btc = btc.history(period = "15y",interval= "1d" ).iloc[:, :5]*10**-6
    btc = btc.history(start=dt.datetime(2020,9,1)-dt.timedelta(days=1729), end =dt.datetime(2025,9,1),interval= "1d" ).iloc[:, :]*10**-6
    
    stats =walk_forward((btc*10**-6),RocAD,
                        maximize='Alpha [%]',
                        constraint=None)
    plot_stats(stats)
    
    """
    bt = Backtest(btc,MOMAD,cash=100,commission=0.01)
    stats=bt.run()
    bt.plot()
    """
    print(stats)
    