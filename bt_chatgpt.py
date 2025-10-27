# strategy_backtest.py
"""
Estrategia cuant: EMA crossover + filtro de momentum (RSI + retorno pasado) + stop ATR (Chandelier-style).
Lista de dependencias:
    pip install backtesting yfinance pandas numpy

Ejecutar:
    python strategy_backtest.py
"""
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
from math import isnan
import talib
import datetime as dt
from backtesting.lib import crossover, TrailingStrategy, MultiBacktest, resample_apply
# --------------------------
# Parámetros (ajustables)
# --------------------------
SHORT_EMA = 20 # periodo EMA corto (tendencia rápida)
LONG_EMA = 50 # periodo EMA largo (tendencia lenta)
RSI_PERIOD = 14 # periodo RSI
RSI_THRESHOLD = 50 # usar como filtro (por encima = tendencia alcista)
MOM_WINDOW = 12 # meses (usamos 12-1 días approximado) -> para series diarias usaremos 252/12 ~ 21 periodos para 1 month
ATR_PERIOD = 14 # ATR para medir volatilidad
ATR_MULT = 3.0 # multiplicador para Chandelier-style stop

# --------------------------
# Indicadores helpers
# --------------------------
def ema(series, span):
    """Exponential moving average (pandas ewm)."""
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    """Relative Strength Index (Wilder's method)."""
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def atr(df, period=14):
    """Average True Range using High, Low, Close."""
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

# --------------------------
# Strategy definition
# --------------------------
class EMAMomentumATR(Strategy):
    """
    Reglas:
      - Señal de compra: EMA_short cruza por encima de EMA_long
        + filtro: RSI > RSI_THRESHOLD (indica momentum positivo) OR retorno pasado > 0
      - Señal de venta: EMA_short cruza por debajo de EMA_long OR precio cae por debajo del stop ATR (Chandelier)
      - Stop dinámico (Chandelier-style): para posición larga, stop = highest_high - ATR_MULT * ATR
    """
    def init(self):
        
        # Indicadores calculados una sola vez y guardados
        self.ema_short = self.I(talib.EMA, self.data.Close, SHORT_EMA)
        self.ema_long = self.I(talib.EMA, self.data.Close, LONG_EMA)
        self.rsi = self.I(talib.RSI, self.data.Close, RSI_PERIOD)
        self.atr = self.I(talib.ATR, self.data.High,self.data.Low,self.data.Close, ATR_PERIOD)
        # Para momentum simple: retorno acumulado en ventana MOM_WINDOW
        # Si tus datos son diarios, MOM_WINDOW aquí será en días (ajusta si quieres meses)
        self.mom = self.I(talib.MOM, self.data.Close, MOM_WINDOW)

    def next(self):
        price = self.data.Close[-1]
        ema_s = self.ema_short[-1]
        ema_l = self.ema_long[-1]
        rsi_v = self.rsi[-1]
        atr_v = self.atr[-1]

        # Chandelier stop (para largos): usar máximo de N barras
        # Aquí usamos LONG_EMA como proxy de ventana para el máximo reciente; se puede ajustar.
        lookback = LONG_EMA
        highest_high = self.data.High[-lookback:].max()
        chandelier_stop = highest_high - ATR_MULT * atr_v if not isnan(atr_v) else -np.inf

        # Señal de entrada: cruce al alza
        if crossover(self.ema_short, self.ema_long):
            momentum_ok = (rsi_v > RSI_THRESHOLD) or (self.mom[-1] > 0)
            if momentum_ok:
                # Abrimos posición larga con todo el capital disponible
                # Se podría usar sizing más sofisticado (Kelly, risk parity, fixed fraction)
                self.position.close() # cerrar posiciones contrarias si hubiese
                self.buy()

        # Señal de salida: cruce a la baja o stop activado
        if self.position.is_long:
            # si cruza a la baja -> salir
            if crossover(self.ema_long, self.ema_short):
                self.position.close()
            # si precio baja por debajo del stop -> salir
            elif price < chandelier_stop:
                self.position.close()

# --------------------------
# Ejecución de ejemplo (descarga datos con yfinance)
# --------------------------
if __name__ == "__main__":
    # Ejemplo: usar ticker AAPL (puedes cambiar por cualquier ETF o acción líquida)
    # backtesting.py requiere columnas: Open, High, Low, Close, Volume
    """
    df = yf.Ticker('BTC-USD')
    #btc = btc_data.history(start=dt.datetime(2025,8,12)-dt.timedelta(days=728), end =dt.datetime(2025,8,11),interval= "4h" ).iloc[:, :4]*10**-6
    #btc 
    df = df.history(start = dt.datetime(2015,1,1),
                        end=dt.datetime(2025,8,17), 
                        interval="1d").iloc[:, :4]
    

    bt = Backtest(df, EMAMomentumATR, cash=100000, commission=0.0005, trade_on_close=False, exclusive_orders=True)
    stats = bt.run()
    print(stats) # muestra métricas estándar: Return, Drawdown, Sharpe, etc.
    bt.plot() # abre ventana interactiva (si corres en entorno gráfico)
    """
    # NOTA:
    # - Ajusta SHORT_EMA, LONG_EMA, ATR_MULT y MOM_WINDOW según el activo.
    # - Para evaluar robustez: realizar walk-forward, cross-validation temporal y test en out-of-sample.
    btc= yf.Ticker("btc-USD")
    btc_data = btc.history(start = dt.datetime(2015,1,1),
                        end=dt.datetime(2025,8,17), 
                        interval="1d")
    btc_data
    # %%
    BTC = yf.Ticker("BTC-USD")
    btc = BTC.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    ETH = yf.Ticker("ETH-USD")
    eth = ETH.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                    interval="1d").iloc[:, :]*10**-6
    BNB = yf.Ticker("BNB-USD")
    bnb = BNB.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    DOT = yf.Ticker("DOT-USD")
    dot = DOT.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    CAKE = yf.Ticker("CAKE-USD")
    cake = CAKE.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    XAUUSD = yf.Ticker("XAUT-USD")
    xau= XAUUSD.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    COIN = yf.Ticker("COIN")
    coin = COIN.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    NVDA = yf.Ticker("NVDA")
    nvda = NVDA.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    AAPL = yf.Ticker("AAPL")
    aapl = AAPL.history(start=dt.datetime(2015, 1, 1),
                            end=dt.datetime(2025, 9, 1),
                            interval="1d").iloc[:, :]*10**-6
    
    btm = MultiBacktest([btc,eth,bnb,dot,cake,xau,coin,nvda,aapl],EMAMomentumATR,cash=10, commission=.01)
    stats=btm.run()
    print(stats)