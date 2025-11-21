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

# Define tickers and date range
TICKERS = ["BTC-USD", "ETH-USD", "BNB-USD", "DOT-USD", "CAKE-USD", "XAUT-USD", "COIN", "NVDA", "AAPL"]
START_DATE = dt.datetime(2015, 1, 1)
END_DATE = dt.datetime(2024, 10, 31)

# Fetch data for all tickers
data = {}
for ticker in TICKERS:
    data[ticker.lower().replace("-", "")] = yf.Ticker(ticker).history(
        start=START_DATE, 
        end=END_DATE, 
        interval="1d"
    ).iloc[:, :] * 10**-6

# Unpack for backward compatibility
btc, eth, bnb, dot, cake, xau, coin, nvda, aapl = data.values()


# %%
class BTKAMA(Strategy):
    n1 = 11
    n2 = 22
    stop = 100
    #
    opt_ranges = {
        'n1': range(2, 4, 1),
        'n2': range(2, 4, 1),
        'stop': range(2, 4, 1)}

    def init(self):
        self.kama1 = self.I(talib.KAMA, self.data.Close, self.n1)
        self.kama2 = self.I(talib.KAMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.kama1, self.kama2):
            self.position.close()
            self.buy(sl=(self.data.Close-self.data.Close*(self.stop/100)))
        elif crossover(self.kama2, self.kama1):
            self.position.close()
            self.sell(sl=(self.data.Close+self.data.Close*(self.stop/100)))
       
if __name__=="__main__":
    backtesting.Pool = multiprocessing.Pool
    
    # Run walk-forward optimization on BTC
    print("Running walk-forward optimization...")
    stats = walk_forward(
        btc,
        BTKAMA,
        maximize='Sharpe Ratio',
        constraint=lambda p: p.n1 < p.n2
    )
    plot_stats(stats)
    """
    print("Walk-forward optimization completed.")
    # Run backtest on BTC with optimized parameters
    bt = Backtest(btc * 10**-6, BTKAMA, cash=10, commission=0.001)
    stat = bt.run()
    bt.plot(filename='results/bt_kama.html')
    print("BTC Backtest Results:")
    print(stat)

    # Run multi-asset backtest
    print("\nRunning multi-asset backtest...")
    btm = MultiBacktest(
        [btc, eth, bnb, dot, cake, xau, coin, nvda, aapl],
        BTKAMA,
        cash=10,
        commission=0.001
    )
    stats = btm.run()
    print(stats)
    
    # Save results to CSV with timestamp
    stats_df = pd.DataFrame(stats)
    timestamp = int(time.time())
    output_file = f'data/backtest_results_{timestamp}.csv'
    stats_df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
    """



