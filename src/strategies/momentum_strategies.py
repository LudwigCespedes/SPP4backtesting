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


