"""
Estrategias basadas en KAMA (Kaufman Adaptive Moving Average).
"""
import os
from backtesting import Strategy
from backtesting.lib import crossover
import talib

from src.strategies.base_strategies import BaseStrategy


class KamaStrategy(BaseStrategy):
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


class KAMACrossover(Strategy):
    """
    Estrategia de cruce de dos KAMAs con stop loss y take profit.
    
    Usa dos KAMAs de diferentes períodos para generar señales.
    Incluye gestión de riesgo con SL/TP dinámicos.
    """
    
    n1 = 11
    n2 = 22
    stop = 10
    profit = 20
    
    opt_ranges = {
        'n1': range(5, 50, 5),      # 9 values: 5, 10, 15, ..., 45
        'n2': range(10, 100, 10),   # 9 values: 10, 20, 30, ..., 90
        'stop': range(2, 50, 2),    # 9 values: 5, 10, 15, ..., 45
        'profit': range(4, 50, 2) # 9 values: 10, 20, 30, ..., 90
    }
    # Total combinations: 9 × 9 × 9 × 9 = 6,561 (manageable)

    def init(self):
        """Inicializa indicadores."""
        self.kama1 = self.I(talib.KAMA, self.data.Close, self.n1)
        self.kama2 = self.I(talib.KAMA, self.data.Close, self.n2)

    def next(self):
        """Lógica de trading."""
        # Cruce alcista
        if crossover(self.kama1, self.kama2):
            self.position.close()
            self.buy(
                sl=(self.data.Close - self.data.Close * (self.stop / 100)),
                tp=(self.data.Close + self.data.Close * (self.profit / 100))
            )
        
        # Cruce bajista
        elif crossover(self.kama2, self.kama1):
            self.position.close()
            self.sell(
                sl=(self.data.Close + self.data.Close * (self.stop / 100)),
                tp=(self.data.Close - self.data.Close * (self.profit / 100))
            )