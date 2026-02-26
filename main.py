from SPP4backtesting.strategies.sma_strategies import BTSMAStrategy
from SPP4backtesting.utils.optimization import walk_forward
import yfinance as yf
import datetime as dt

SYMBOL = "BTC-USD"
START_DATE = dt.datetime(2015, 1, 1)
END_DATE = dt.datetime(2025, 12, 31)
INTERVAL = "1d"


BTC = yf.Ticker(SYMBOL)
btc = BTC.history(start=START_DATE, end=END_DATE, interval=INTERVAL)


btc.head()
df = btc
print(walk_forward(df,BTSMAStrategy,17,0.01))
    
def main():
    print("Hello from spp4backtesting!")

"""
if __name__ == "__main__":
    main()
    """
