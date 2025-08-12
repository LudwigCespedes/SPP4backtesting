# %%
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy, resample_apply
import backtesting
import yfinance as yf
import datetime as dt
import talib
import matplotlib.pyplot as plt
import pandas as pd
btc= yf.Ticker("BTC-USD")
btc_data = btc.history(start = dt.datetime.now()-dt.timedelta(days=700),
                       end=dt.datetime.now(), 
                       interval="4h")
btc_data
# %%
data = pd.read_csv('data.csv', index_col='timestamp', parse_dates=True)

# Renombra columnas si es necesario
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
# %%
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply

def PIVOTS(high, low, close):
    h = high
    l = low
    c = close
    pivot = (h + l + c) / 3
    r1 = (2 * pivot) - l
    s1 = (2 * pivot) - h
    r2 = pivot + (h - l)
    s2 = pivot - (h - l)
    # Devuelve un dict para DataFrame automático
    return {'pivot': pivot, 'r1': r1, 's1': s1, 'r2': r2, 's2': s2}

class SimpleArbitrageUSDCUSDT(Strategy):
    timeperiod = 20  # Periodo para las bandas de Bollinger
    nbdevup = 3  # Desviación estándar para la banda superior
    nbdevdn=2  # Desviación estándar para la banda inferior
    matype = 1  # Tipo de media móvil (1 = SMA)
    amount = 2  # Tamaño de la orden

    def init(self):
        # Calcula las bandas de Bollinger
        close = self.data.Close.s
        open = self.data.Open.s
        high = self.data.High.s
        low = self.data.Low.s
        self.upper, self.middle, self.lower = talib.BBANDS(close, timeperiod=self.timeperiod, 
                                                           nbdevup=self.nbdevup, nbdevdn=self.nbdevdn, 
                                                           matype=self.matype)
        
        # Calcula los pivotes
        pivots = resample_apply("1d", PIVOTS, self.data.High, self.data.Low, self.data.Close)
        self.pivot = pivots['pivot']
        self.r1 = pivots['r1']
        self.s1 = pivots['s1']
        self.r2 = pivots['r2']
        self.s2 = pivots['s2']
        
    def next(self):
        price = self.data.Close.s[-1]
        upper = self.upper[- 1]
        lower = self.lower[- 1]

        # Simula balances (puedes ajustar esto según tu lógica)
        balanse_usdc = 1000
        balanse_usdt = 1000

        if balanse_usdt > self.amount:
            if price < lower:
                self.buy(size=self.amount,tp=upper)

class pivotsusdc_usdt(Strategy):
    def init(self):
        pivots = pd.DataFrame([PIVOTS(self.data.High[i:i+24], self.data.Low[i:i+24], self.data.Close[i:i+24])
                               for i in range(0, len(self.data), 24)])
        pivots = pivots.reindex(range(len(self.data)), method='ffill')  # Forward fill para cada barra
        self.pivot = pivots['pivot'].values
        self.r1 = pivots['r1'].values
        self.s1 = pivots['s1'].values
        self.r2 = pivots['r2'].values
        self.s2 = pivots['s2'].values
        self.in_r1_trade = False
        self.in_s2_trade = False

    def next(self):
        price = self.data.Close[-1]

        # Compra en R1, vende en R2
        if not self.in_r1_trade and crossover(self.data.Close, self.r1):
            if self.r2[-1] > price:
                self.buy(size=2, tp=self.r2[-1])
                self.in_r1_trade = True

        if self.in_r1_trade and crossover(self.data.Close, self.r2):
            self.position.close()
            self.in_r1_trade = False

        # Compra en S2, vende en S1 (solo si S1 > S2)
        if not self.in_s2_trade and crossover(self.data.Close, self.s2):
            if self.s1[-1] > price:
                self.buy(size=2, tp=self.s1[-1])
                self.in_s2_trade = True

        if self.in_s2_trade and crossover(self.data.Close, self.s1):
            self.position.close()
            self.in_s2_trade = False
            
if __name__ == "__main__":
    # Carga tus datos OHLCV (asegúrate de tener un archivo 'data.csv' con columnas: Open, High, Low, Close, Volume)
    bt = Backtest(btc_data, pivotsusdc_usdt, cash=10000, commission=0)
    """
    stats = bt.optimize(
        timeperiod=range(2, 100),
        nbdevup=range(1, 5),
        nbdevdn=range(1, 5),
        matype=range(0, 5),
        amount=range(1, 10),
        maximize='Return [%]',
        constraint=lambda p: p.nbdevup > p.nbdevdn  )
    print(stats)
    """
    stats = bt.run()
    print(stats)
    bt.plot()