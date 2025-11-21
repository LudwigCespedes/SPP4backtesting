# btc_daily_sma_adx_atr.py
"""
SMA(50,200) + ADX filter + ROC momentum + ATR stops + volatility-based sizing
Diseñado para BTC (daily). Usa TA-Lib para indicadores.
"""

import math
import numpy as np
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf

# -------------------------
# Parámetros por defecto (ajustables)
# -------------------------
FAST_SMA = 50
SLOW_SMA = 200
ADX_PERIOD = 14
ADX_THRESHOLD = 25
ROC_PERIOD = 21        # momentum (21 días ~ 1 mes trading days)
ATR_PERIOD = 14
STOP_MULT = 4.0        # stop = ATR * STOP_MULT
TP_MULT = 10.0         # tp = ATR * TP_MULT
RISK_PER_TRADE = 0.01  # 1% del equity por trade
COMMISSION = 0.00075   # 0.075% por trade (ajusta según exchange)
MIN_SIZE = 1e-8        # tamaño mínimo para abrir posición (BTC permite fraccionario)

# -------------------------
# Estrategia
# -------------------------
class BTC_SMA_ADX_ATR(Strategy):
    # Parametrizables para optimización
    fast_sma = FAST_SMA
    slow_sma = SLOW_SMA
    adx_period = ADX_PERIOD
    adx_thresh = ADX_THRESHOLD
    roc_period = ROC_PERIOD
    atr_period = ATR_PERIOD
    stop_mult = STOP_MULT
    tp_mult = TP_MULT
    risk_per_trade = RISK_PER_TRADE

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        # Indicadores TA-Lib
        self.sma_fast = self.I(talib.SMA, close, self.fast_sma)
        self.sma_slow = self.I(talib.SMA, close, self.slow_sma)
        self.adx = self.I(talib.ADX, high, low, close, self.adx_period)
        self.roc = self.I(talib.ROC, close, self.roc_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)

    def _size_by_volatility(self, price, atr):
        """
        Calcula tamaño (en unidades de BTC) para arriesgar `risk_per_trade` del equity.
        size = (equity * risk_per_trade) / (stop_distance)
        stop_distance = atr * stop_mult
        """
        if atr is None or atr <= 0:
            return 0.0
        equity = self.equity
        dollar_risk = equity * self.risk_per_trade
        stop_distance = max(atr * self.stop_mult, 1e-9)
        size = dollar_risk / stop_distance
        # En BTC podemos operar fracciones, pero imponemos un mínimo
        return size if size >= MIN_SIZE else 0.0

    def next(self):
        price = self.data.Close[-1]
        atr_v = self.atr[-1]
        adx_v = self.adx[-1]
        roc_v = self.roc[-1]

        # Validación de indicadores
        if np.isnan(atr_v) or np.isnan(adx_v) or np.isnan(roc_v):
            return

        long_cross = crossover(self.sma_fast, self.sma_slow)
        short_cross = crossover(self.sma_slow, self.sma_fast)

        # Filtros: ADX y ROC
        long_signal = long_cross and (adx_v > self.adx_thresh) and (roc_v > 0)
        short_signal = short_cross and (adx_v > self.adx_thresh) and (roc_v < 0)

        # Tamaño por volatilidad
        size = self._size_by_volatility(price, atr_v)

        # Ejecutar LONG
        if long_signal and size > 0:
            # cerrar shorts existentes
            if self.position.is_short:
                self.position.close()
            sl = price - atr_v * self.stop_mult
            tp = price + atr_v * self.tp_mult
            # backtesting.py acepta size en unidades (float OK)
            self.buy(size=size, sl=sl, tp=tp)

        # Ejecutar SHORT
        elif short_signal and size > 0:
            if self.position.is_long:
                self.position.close()
            sl = price + atr_v * self.stop_mult
            tp = price - atr_v * self.tp_mult
            self.sell(size=size, sl=sl, tp=tp)

# -------------------------
# Descargar datos y ejecutar (ejemplo con yfinance)
# -------------------------
if __name__ == "__main__":
    # Ticker Yahoo para Bitcoin spot
    ticker = "BTC-USD"
    print("Descargando datos diarios para:", ticker)
    # Periodo: ajusta según necesites
    df = yf.download(ticker, start="2015-01-01", end=None, interval="1d")
    df = df.dropna()
    print("Filas descargadas:", len(df))

    bt = Backtest(df, BTC_SMA_ADX_ATR,
                  cash=100000,             # capital inicial en USD
                  commission=COMMISSION,
                  trade_on_close=False,
                  exclusive_orders=True)

    stats = bt.run()
    print(stats)
    bt.plot()

