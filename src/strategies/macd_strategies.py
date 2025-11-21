"""
Estrategias basadas en MACD (Moving Average Convergence Divergence).

Consolida todas las estrategias que usan MACD como indicador principal.
"""

from backtesting import Strategy
from backtesting.lib import crossover, resample_apply
import talib


class MacdAdxEmaStrategy(Strategy):
    """
    Estrategia MACD + ADX + EMA.
    
    Usa MACD para señales de entrada/salida, ADX para filtrar tendencias,
    y EMAs de diferentes períodos para determinar dirección de tendencia.
    
    Basada en: bt_macd_adx_ema.py
    """
    
    # Parámetros de la estrategia
    macdfast = 12
    macdslow = 26
    macdsignal = 9
    adxperiod = 14
    emafast = 9
    emalow = 50
    adxpass = 20
    
    # Rangos para optimización
    opt_ranges = {
        "macdfast": range(10, 13),
        "macdslow": range(20, 26),
        "macdsignal": range(11, 13),
        "adxperiod": range(5, 21, 2),
        "emafast": range(10, 100, 10),
        "emalow": range(10, 200, 10),
        "adxpass": range(10, 90, 10)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.macd = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.macdfast,
            slowperiod=self.macdslow,
            signalperiod=self.macdsignal
        )
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.adxperiod
        )
        self.ema1period30mf = resample_apply(
            '7d',
            talib.EMA,
            self.data.Close.s,
            self.emafast
        )
        self.ema2period30ml = resample_apply(
            '7d',
            talib.EMA,
            self.data.Close,
            self.emalow
        )
    
    def next(self):
        """Lógica de trading."""
        # Tendencia alcista
        if (self.adx > self.adxpass) and (self.ema1period30mf > self.ema2period30ml):
            if self.position.is_short:
                self.position.close()
            if crossover(self.macd[0], self.macd[1]):
                self.buy()
            elif crossover(self.macd[1], self.macd[0]):
                self.position.close()
        
        # Tendencia bajista
        elif (self.adx > self.adxpass) and (self.ema1period30mf < self.ema2period30ml):
            if self.position.is_long:
                self.position.close()
            if crossover(self.macd[1], self.macd[0]):
                self.sell()
            elif crossover(self.macd[0], self.macd[1]):
                self.position.close()
        
        # Sin tendencia clara
        elif self.adx < self.adxpass:
            self.position.close()


class MacdAdxStrategy(Strategy):
    """
    Estrategia MACD + ADX simplificada.
    
    Usa MACD para señales y ADX para filtrar tendencias débiles.
    
    Basada en: bt_macd_adx.py
    """
    
    macdfast = 12
    macdslow = 26
    macdsignal = 9
    adxperiod = 14
    adxpass = 25
    
    opt_ranges = {
        "macdfast": range(8, 15),
        "macdslow": range(20, 30),
        "macdsignal": range(7, 12),
        "adxperiod": range(10, 20),
        "adxpass": range(20, 40, 5)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.macd = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.macdfast,
            slowperiod=self.macdslow,
            signalperiod=self.macdsignal
        )
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.adxperiod
        )
    
    def next(self):
        """Lógica de trading."""
        if self.adx > self.adxpass:
            if crossover(self.macd[0], self.macd[1]):
                if self.position.is_short:
                    self.position.close()
                self.buy()
            elif crossover(self.macd[1], self.macd[0]):
                if self.position.is_long:
                    self.position.close()
                self.sell()
        else:
            self.position.close()


class MacdStrategy(Strategy):
    """
    Estrategia MACD simple.
    
    Usa solo MACD para generar señales de compra/venta.
    
    Basada en: btmacd.py
    """
    
    fast = 12
    slow = 26
    signal = 9
    
    opt_ranges = {
        "fast": range(8, 15),
        "slow": range(20, 35),
        "signal": range(7, 12)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.macd = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.fast,
            slowperiod=self.slow,
            signalperiod=self.signal
        )
    
    def next(self):
        """Lógica de trading."""
        if crossover(self.macd[0], self.macd[1]):
            if self.position.is_short:
                self.position.close()
            self.buy()
        elif crossover(self.macd[1], self.macd[0]):
            if self.position.is_long:
                self.position.close()
            self.sell()


class MacdAdxSmaStrategy(Strategy):
    """
    Estrategia MACD + ADX + SMA.
    
    Combina MACD, ADX y SMAs para filtrar señales.
    
    Basada en: btmacd_adx.py
    """
    
    macdfast = 12
    macdslow = 26
    macdsignal = 9
    adxperiod = 14
    smafast = 20
    smaslow = 50
    adxpass = 25
    
    opt_ranges = {
        "macdfast": range(8, 15),
        "macdslow": range(20, 30),
        "macdsignal": range(7, 12),
        "adxperiod": range(10, 20),
        "smafast": range(10, 30),
        "smaslow": range(40, 100, 10),
        "adxpass": range(20, 40, 5)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.macd = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=self.macdfast,
            slowperiod=self.macdslow,
            signalperiod=self.macdsignal
        )
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.adxperiod
        )
        self.sma_fast = self.I(talib.SMA, self.data.Close, self.smafast)
        self.sma_slow = self.I(talib.SMA, self.data.Close, self.smaslow)
    
    def next(self):
        """Lógica de trading."""
        # Solo operar con tendencia fuerte
        if self.adx > self.adxpass:
            # Tendencia alcista
            if self.sma_fast > self.sma_slow:
                if crossover(self.macd[0], self.macd[1]):
                    if self.position.is_short:
                        self.position.close()
                    self.buy()
                elif crossover(self.macd[1], self.macd[0]):
                    self.position.close()
            
            # Tendencia bajista
            elif self.sma_fast < self.sma_slow:
                if crossover(self.macd[1], self.macd[0]):
                    if self.position.is_long:
                        self.position.close()
                    self.sell()
                elif crossover(self.macd[0], self.macd[1]):
                    self.position.close()
        else:
            self.position.close()
