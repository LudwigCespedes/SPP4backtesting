"""
Estrategias basadas en indicadores de momentum.

Incluye estrategias que usan KAMA, Momentum, Regresión Lineal, etc.
"""

from backtesting import Strategy
from backtesting.lib import crossover
import talib
import numpy as np


class MomentumStrategy(Strategy):
    """
    Estrategia basada en el indicador de Momentum.
    
    Usa el momentum para detectar cambios en la tendencia.
    
    Basada en: bt_mom.py
    """
    
    period = 14
    threshold = 0
    
    opt_ranges = {
        'period': range(5, 30),
        'threshold': range(-10, 10)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.momentum = self.I(talib.MOM, self.data.Close, timeperiod=self.period)
    
    def next(self):
        """Lógica de trading."""
        if self.momentum > self.threshold:
            if self.position.is_short:
                self.position.close()
            if not self.position:
                self.buy()
        elif self.momentum < -self.threshold:
            if self.position.is_long:
                self.position.close()
            if not self.position:
                self.sell()


class KamaStrategy(Strategy):
    """
    Estrategia basada en KAMA (Kaufman Adaptive Moving Average).
    
    KAMA se adapta a la volatilidad del mercado.
    
    Basada en: bt_kama.py
    """
    
    period = 10
    
    opt_ranges = {
        'period': range(5, 50, 5)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.kama = self.I(talib.KAMA, self.data.Close, timeperiod=self.period)
    
    def next(self):
        """Lógica de trading."""
        # Compra cuando el precio cruza por encima de KAMA
        if crossover(self.data.Close, self.kama):
            if self.position.is_short:
                self.position.close()
            self.buy()
        
        # Venta cuando el precio cruza por debajo de KAMA
        elif crossover(self.kama, self.data.Close):
            if self.position.is_long:
                self.position.close()
            self.sell()


class LinearRegressionStrategy(Strategy):
    """
    Estrategia basada en Regresión Lineal.
    
    Usa la pendiente de la regresión lineal para determinar tendencia.
    
    Basada en: bt_linear_regression.py
    """
    
    period = 20
    
    opt_ranges = {
        'period': range(10, 50, 5)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.linreg = self.I(
            talib.LINEARREG,
            self.data.Close,
            timeperiod=self.period
        )
        self.linreg_slope = self.I(
            talib.LINEARREG_SLOPE,
            self.data.Close,
            timeperiod=self.period
        )
    
    def next(self):
        """Lógica de trading."""
        # Compra si la pendiente es positiva
        if self.linreg_slope > 0:
            if self.position.is_short:
                self.position.close()
            if not self.position:
                self.buy()
        
        # Venta si la pendiente es negativa
        elif self.linreg_slope < 0:
            if self.position.is_long:
                self.position.close()
            if not self.position:
                self.sell()
