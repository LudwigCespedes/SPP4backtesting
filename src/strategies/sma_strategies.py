"""
Estrategias basadas en SMA (Simple Moving Average).

Consolida estrategias que usan SMAs como indicador principal.
"""

from backtesting import Strategy
from backtesting.lib import crossover
import talib
from src.strategies.base_strategies import BaseStrategy

class BTSMAStrategy(BaseStrategy):
    """
    Estrategia de cruce de SMAs con stop loss y take profit.
    
    Usa dos SMAs de diferentes períodos para generar señales.
    Incluye gestión de riesgo con SL/TP dinámicos.
    
    Basada en: btsma.py
    """
    
    n1 = 11
    n2 = 22
    stop = 2  # Porcentaje de stop loss
    profit = 4  # Porcentaje de take profit
    
    opt_ranges = {
        'n1': range(2, 50, 2),        # Períodos de SMA rápida
        'n2': range(2, 50, 2),      # Períodos de SMA lenta
        'stop': range(1, 50, 5),       # Stop loss: 1% a 20%
        'profit': range(2, 100, 5)      # Take profit: 2% a 30%
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)
    
    def next(self):
        """Lógica de trading."""
        # Cruce alcista
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy(
                sl=(self.data.Close - self.data.Close * (self.stop / 100)),
                tp=(self.data.Close + self.data.Close * (self.profit / 100))
            )
        
        # Cruce bajista
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell(
                sl=(self.data.Close + self.data.Close * (self.stop / 100)),
                tp=(self.data.Close - self.data.Close * (self.profit / 100))
            )


class SmaAdxStrategy(BaseStrategy):
    """
    Estrategia SMA + ADX.
    
    Combina SMAs para dirección de tendencia y ADX para fuerza.
    
    Basada en: bt_sma_adx.py
    """
    
    smafast = 20
    smaslow = 50
    adxperiod = 14
    adxpass = 25
    
    opt_ranges = {
        'smafast': range(10, 50, 5),
        'smaslow': range(40, 200, 10),
        'adxperiod': range(10, 20),
        'adxpass': range(20, 40, 5)
    }
    
    def init(self):
        """Inicializa indicadores."""
        self.sma_fast = self.I(talib.SMA, self.data.Close, self.smafast)
        self.sma_slow = self.I(talib.SMA, self.data.Close, self.smaslow)
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.adxperiod
        )
    
    def next(self):
        """Lógica de trading."""
        # Solo operar con tendencia fuerte
        if self.adx > self.adxpass:
            # Cruce alcista
            if crossover(self.sma_fast, self.sma_slow):
                if self.position.is_short:
                    self.position.close()
                self.buy()
            
            # Cruce bajista
            elif crossover(self.sma_slow, self.sma_fast):
                if self.position.is_long:
                    self.position.close()
                self.sell()
        else:
            # Cerrar posiciones en mercado lateral
            self.position.close()
