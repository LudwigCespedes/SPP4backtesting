from backtesting import Strategy
from backtesting.lib import crossover, resample_apply
import talib

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
