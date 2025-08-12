# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import backtesting
import yfinance as yf
import datetime as dt
import talib



# %%
spy_data = yf.Ticker('spy')
spy = spy_data.history(period='max').iloc[:, :5]

# %%
class Rsi0scillator(Strategy):
    lower_band = 30
    upper_band = 70
    rsi_window = 14
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_window)

    def next(self):
        if crossover(self.rsi, self.upper_band):
            self.position.close()
        elif crossover(self.rsi, self.lower_band):
            self.buy()
bt = Backtest(spy, Rsi0scillator, cash=1000, commission=.02)
stat = bt.optimize(
    rsi_window=range(10, 30, 2),
    upper_band=range(50, 85, 5),
    lower_band=range(10, 30, 2),
    maximize='Return [%]',
    constraint= lambda p: p.upper_band > p.lower_band)
print(stat)
bt.plot()


