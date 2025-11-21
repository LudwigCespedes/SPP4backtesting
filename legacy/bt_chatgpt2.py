"""
Estrategia cuantitativa basada en:
- Cruce de SMA (tendencia)
- Filtro de Momentum + RSI
- Stop-loss / Take-profit dinámicos con ATR
- Basado en tu plantilla BTSMA, pero mejorado
"""

import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib


class QuantSMA_MomentumATR(Strategy):
    # Parámetros optimizables
    n1 = 11
    n2 = 100
    atr_period = 14
    stop_mult = 3       # múltiplos de ATR para stop-loss
    tp_mult = 8         # múltiplos de ATR para take-profit
    mom_period = 20     # días para momentum

    # Rango para optimización
    opt_ranges = {
        'n1': range(5, 50, 1),
        'n2': range(20, 200, 1),
        'atr_period': range(5, 50, 1),
        'stop_mult': range(1, 10, 1),
        'tp_mult': range(2, 20, 1),
        'mom_period': range(5, 40, 1),
    }

    def init(self):
        close = self.data.Close

        # Medias móviles (indicador principal)
        self.sma1 = self.I(talib.SMA, close, self.n1)
        self.sma2 = self.I(talib.SMA, close, self.n2)

        # RSI como filtro de sobrecompra/sobreventa
        self.rsi = self.I(talib.RSI, close, 14)

        # Momentum / rate of change
        self.mom = self.I(talib.ROC, close, self.mom_period)

        # ATR para stops dinámicos
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, close, self.atr_period)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]

        # Señal LONG: cruce alcista + momentum positivo + RSI saludable
        long_signal = (
            crossover(self.sma1, self.sma2) and 
            self.mom[-1] > 0 and 
            self.rsi[-1] < 70
        )

        # Señal SHORT: cruce bajista + momentum negativo + RSI saludable
        short_signal = (
            crossover(self.sma2, self.sma1) and
            self.mom[-1] < 0 and
            self.rsi[-1] > 30
        )

        # Stops dinámicos
        sl_long = price - atr * self.stop_mult
        tp_long = price + atr * self.tp_mult
        sl_short = price + atr * self.stop_mult
        tp_short = price - atr * self.tp_mult

        # Entrada LONG
        if long_signal:
            self.position.close()
            self.buy(sl=sl_long, tp=tp_long)

        # Entrada SHORT
        elif short_signal:
            self.position.close()
            self.sell(sl=sl_short, tp=tp_short)
if __name__ == "__main__":
    import yfinance as yf
    import datetime as dt
    from backtesting import Backtest

    # Descargar datos de BTC-USD
    btc = yf.Ticker("BTC-USD")
    data = btc.history(start=dt.datetime(2020, 1, 1),
                       end=dt.datetime(2025, 11, 17),
                       interval="1d").iloc[:, :]*10**-6
    """
    data = btc.history(start = dt.datetime.now()-dt.timedelta(days=700),
                       end=dt.datetime.now(), 
                       interval="1h").iloc[:, :]*10**-6
                       """

    # Ejecutar backtest
    bt = Backtest(data, QuantSMA_MomentumATR, cash=1000, commission=0.001,margin=1)
    stats = bt.run()
    bt.plot()
    print(stats)