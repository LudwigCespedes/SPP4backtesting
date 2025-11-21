"""
Estrategias de Grid Trading.

Grid trading coloca órdenes de compra y venta en niveles de precio predefinidos.
"""

from backtesting import Strategy
import talib


class GridStrategy(Strategy):
    """
    Estrategia de Grid Trading.
    
    Coloca órdenes de compra y venta en niveles de precio predefinidos
    para aprovechar la volatilidad del mercado en rangos.
    
    Basada en: bt_grid.py
    """
    
    grid_profit = 1  # Porcentaje de ganancia por grid
    grid_buy = 10  # Número de niveles de compra
    
    opt_ranges = {
        'grid_profit': range(1, 5),
        'grid_buy': range(5, 20)
    }
    
    def init(self):
        """Inicializa la estrategia."""
        self.grid_levels = []
        self.initial_price = None
    
    def next(self):
        """Lógica de trading."""
        # Establecer precio inicial
        if self.initial_price is None:
            self.initial_price = self.data.Close[-1]
            # Crear niveles de grid
            for i in range(1, self.grid_buy + 1):
                level = self.initial_price * (1 - (i * self.grid_profit / 100))
                self.grid_levels.append(level)
        
        current_price = self.data.Close[-1]
        
        # Comprar en niveles de grid
        for level in self.grid_levels:
            if current_price <= level and not self.position:
                target_price = level * (1 + self.grid_profit / 100)
                self.buy(tp=target_price)
                break
